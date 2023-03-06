import asyncio
import datetime
import os

import aiohttp.web
from aiohttp import (
    web,
    ClientSession,
    web_exceptions,
    client_exceptions
)

from xml.etree import ElementTree
from urllib.parse import unquote
from typing import Tuple

from main import log
from config import cfg


class XMLParser:
    """
    The XMLParser class consists of two methods: self.modify_xml() and self.get_correct_date().
    modify_xml() takes one parameter, an XML string and creates an ElementTree object
    from it, extracts the date value,

    then passes it to get_correct_date() to be parsed
    against the current date. If the dates match, get_correct_date() will return an
    unedited XML string as well as a boolean value False telling modify_xml() to return
    the original unedited XML payload.

    If the dates do not match, get_correct_date() will update
    the date value in the XML to reflect current date and return it as a string.

    """

    async def modify_xml(self, xml: str) -> str:
        task_id = asyncio.current_task().get_name()

        try:
            log.debug('Parsing XML.', extra={'task_id': task_id})
            xml_data = ElementTree.fromstring(xml)

            log.info(f'EventID: {xml_data.find("EventID").text}', extra={'task_id': task_id})

            date = xml_data.find('Date')
            date.text, updated = await self.get_correct_date(date.text)

            if updated:
                log.debug('Payload updated.', extra={'task_id': task_id})
                xml_str = ElementTree.tostring(xml_data, encoding='unicode', method='xml')

                return xml_str
            else:
                log.debug('No modifications made to XML payload.', extra={'task_id': task_id})
                return xml

        except ElementTree.ParseError as e:
            log.error(f'Detected XML payload errors: {e}', extra={'task_id': task_id})
            log.error('Unable to update Date value.', extra={'task_id': task_id})

            return xml

    @staticmethod
    async def get_correct_date(date_text: str) -> Tuple[str, bool]:
        task_id = asyncio.current_task().get_name()
        today = datetime.date.today()

        log.info('Performing date comparison.', extra={'task_id': task_id})
        log.debug(f'Verifying date value -> Payload date: {date_text} | Current date: {today.__str__()}',
                  extra={'task_id': task_id})

        try:
            # Compare payload date to current date
            if datetime.date.fromisoformat(date_text) != today:
                log.debug('Updating payload to reflect current date.', extra={'task_id': task_id})
                return today.__str__(), True
            else:
                log.debug('Current date verified.')
                return date_text, False

        except (ValueError, NameError, TypeError) as e:
            log.error(f'Conversion failed: {e}', extra={'task_id': task_id})
            return date_text, False


class Forwarder:
    def __init__(self):
        """
        The Forwarder class is an adaptation of a recommended Handler class as specified within the aiohttp
        documentation. It implements two queues: an incoming queue and outgoing queue. Requests received by the
        application will be placed in the incoming queue by the handler() method.

        The contained xml payload will be processed by the process_incoming() method, then placed in the outgoing
        queue to be sent out by the forward_request() method called by process_outgoing().

        Should any errors occur in process_incoming(), an exception will be raised, and process_outgoing()
        will be cancelled. This assures that both queues always correspond with each other and no conflicts occur.

        """

        self.queue_incoming, self.queue_outgoing = asyncio.Queue(), asyncio.Queue()
        self.xml_parser = XMLParser()

    async def handler(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        log.info('Request received.')

        await self.queue_incoming.put(await self.detect_method(request))

        incoming_task = asyncio.create_task(self.process_incoming())
        outgoing_task = asyncio.create_task(self.process_outgoing())

        incoming_task.set_name(os.urandom(8).hex())
        outgoing_task.set_name(os.urandom(8).hex())

        results = await asyncio.gather(incoming_task, outgoing_task)

        await self.queue_incoming.join()
        await self.queue_outgoing.join()

        return web.Response(text=str(results[1]))

    @staticmethod
    async def detect_method(request: aiohttp.web.Request) -> str:
        xml = None

        log.debug(f'Request method: {request.method}')
        log.debug(f'URL: {unquote(str(request.url))}')

        try:
            if request.method == 'POST':
                request_body = await request.post()

                # If request is conventional POST request (params)
                if request_body:
                    xml = request_body["XMLData"]

                # else POST request contains query strings
                else:
                    request_body = request.query
                    xml = request_body['XMLData']

                log.debug(f'Incoming XML data: {xml}')
                return xml

            if request.method == 'GET':
                xml = request.query['XMLData']

                log.debug(f'Incoming XML data: {xml}')
                return xml

        except KeyError as e:
            log.error(f'Key XMLData not found: {e}')
            raise web.HTTPBadRequest

    async def process_incoming(self):
        task_id = asyncio.current_task().get_name()

        log.info('Processing request payload.', extra={'task_id': task_id})
        payload = await self.queue_incoming.get()
        processed = await self.xml_parser.modify_xml(payload)

        log.debug('Pushing result to outgoing queue.', extra={'task_id': task_id})
        await self.queue_outgoing.put(processed)
        self.queue_incoming.task_done()

    async def process_outgoing(self) -> str:
        task_id = asyncio.current_task().get_name()

        log.info('Forwarding request to QPM.', extra={'task_id': task_id})
        response = await self.forward_request(await self.queue_outgoing.get())
        self.queue_outgoing.task_done()

        return response

    @staticmethod
    async def forward_request(payload: str) -> str:
        task_id = asyncio.current_task().get_name()
        uri = f'{cfg.protocol}://{cfg.target_host}:{cfg.forwarding_port}{cfg.uri}'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        try:
            log.debug(f'Forwarding to {cfg.protocol}://{cfg.target_host}:{cfg.forwarding_port}{cfg.uri}.',
                      extra={'task_id': task_id})

            log.debug(f'Payload: {payload}', extra={'task_id': task_id})

            async with ClientSession() as session:
                async with session.post(
                        url=uri,
                        params={
                            'activity': 'IncomingXML',
                            'XMLData': payload
                        },
                        headers=headers
                ) as response:
                    content = await response.text()
                    log.info(f'Server response: {response.status} | {content}', extra={'task_id': task_id})

                    result = 'SUCCESS' if response.status == 200 else 'FAILED'
                    msg = f'Message forwarding {result}.'
                    log.info(msg, extra={'task_id': task_id})

            await session.close()
            return content

        except web_exceptions.HTTPClientError as e:
            log.error(f'HTTP error: {e}', extra={'task_id': task_id})

        except client_exceptions.ClientOSError as e:
            log.error(f'ClientOS error: {e}', extra={'task_id': task_id})
