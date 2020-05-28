# request wrapper class
"""
    want to make a simple request class wrapper
    to hide a lot of implementaiton
"""

import requests
import xml.etree.ElementTree as ET

# Response class
class HTTPResponse:
    """ response class to capture the detials """

    def __init__(self, response, results, mime_parts):
        """
        Args:
            response (request.response): response object
            results (dict): dictinary of the result tags
            mime_parts (list): the mime_parts of the xml response
        """
        self.response = response
        self.success = response.ok
        self.results = results
        self.mime_parts = mime_parts
        self.value = None

    def __str__(self):
        """ string representation of the response object """
        return f'[Success] {self.success} [Results] {self.value}'

class HTTPRequest(object):

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def send_request(self, method, soap_action, payload, result_tags=['result'], fault_tags=['faultstring']):
        """ send requests using requests module"""

        # TODO: implement method

        try:
            headers = {'SOAPAction': soap_action, 'Content-Type': 'text/xml'}
            http_auth = requests.auth.HTTPBasicAuth(self.username, self.password)

            if method == 'GET':
                response = requests.get(self.url, auth=http_auth, headers=headers)
            elif method == 'POST':
                response = requests.post(self.url, auth=http_auth, headers=headers, data=payload)
        except requests.exceptions.ConnectionError:
            raise Exception(0, "Connection Error!")

        # parse multipart responses
        parts = self._decode_multipart_response(response)

        xml_response = parts[0].decode("utf-8")

        try:
            root = ET.ElementTree(ET.fromstring(xml_response)).getroot()
        except Exception:
            raise ValueError(f'XML Payload from multipart response not valid {xml_response}')

        tags = result_tags if response.ok else fault_tags
        results = self._parse_xml_nodes(root, tags)

        if not response.ok:
            fault_msg = self._parse_fault_string(results['faultstring'])
            raise Exception(fault_msg)

        return HTTPResponse(response, results, parts)

    def _parse_xml_nodes(self, xml_root, nodes_to_select):
        """Parse XML nodes with the nodes specified and returns them as a dictionary"""
        node_values = {}
        for elem in xml_root.iter():
            # if the XML tag contains namespace.
            # TODO: if they do not contain then handle the case
            elem_tag = elem.tag.rpartition('}')[2]
            if elem_tag in nodes_to_select:
                node_values[elem_tag] = elem.text
        return node_values

    def _parse_fault_string(self, fault_str):
        """parse fault string"""

        # find if the fault string contains error message XML
        if fault_str.find('<MESSAGE>') > -1:
            gt = fault_str.find('<MESSAGE>')
            # parse all string before first occurence of <
            err_code = fault_str[:gt].strip()

            # everything after < is the xml part
            part_xml = fault_str[gt:]

            # parse xml - first node of the xml part is error number
            # second part is error message
            #erp_logger.debug(f'XML part for parsing {part_xml}')
            root = ET.ElementTree(ET.fromstring(part_xml)).getroot()
            msg_nbr = root[0].text
            msg_text = root[1].text

            fault_str = f'{err_code} | {msg_nbr} -> {msg_text}'

        return fault_str

    def _decode_multipart_response(self, response):
        """Decode multipart response"""
        body_parts = []

        # throw exception here
        if b'\r\n\r\n' not in response.content:
            body_parts.append(response.content)
            return body_parts

        content_type = response.headers.get('content-type', None)
        content_types = [c.strip() for c in content_type.split(';')]

        for ct in content_types:
            eq_found = ct.find('=')
            attr, val = ct[:eq_found], ct[eq_found + 1:]
            if attr == 'boundary':
                boundary = val.strip('"')
                break
        boundary = bytes(boundary, 'utf-8')
        boundary = b''.join((b'\r\n--', boundary))

        parts = response.content.split(boundary)

        for part in parts:
            p = part.split(b'\r\n\r\n')
            if len(p) > 1:
                body_parts.append(p[1])

        return body_parts
