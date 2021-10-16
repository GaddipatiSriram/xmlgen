from __future__ import print_function

import json
from xml.dom import minidom
from xml.dom.minidom import parse, parseString
import xml.etree.ElementTree as ET

server_xml = 'server.xml'
params_json = 'params.json'
test_json = 'test.json'
tree = ET.parse(server_xml)
root = tree.getroot()

def find(key, dictionary):
    '''
        Does Nested Lookup
    '''
    for k, v in dictionary.items():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in find(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                if isinstance(d, dict):
                    for result in find(key, d):
                        yield result


def has_value(obj, val):
    if isinstance(obj, dict):
        values = obj.values()
    elif isinstance(obj, list):
        values = obj
    if val in values:
        return True
    for v in values:
        if isinstance(v, (dict, list)) and has_value(v, val):
            return True
    return False


def prettify(func):
    def wrapper(*args,**kwargs):
        rough_string = ET.tostring(root, 'utf-8')
        reparsed = parseString(rough_string)
        data = '\n'.join([line for line in reparsed.toprettyxml(indent= ' '*2).split('\n') if line.strip()])
        with open(server_xml, 'w') as f:
            print(data, file =f)
        response = func(*args)
        return response
    return wrapper


def run_all(func):
    def wrapper(*args,**kwargs):
        print("Hello World!!")
        response = func(*args)
        return response
    return wrapper



class Params(object):
    def __init__(self):
        self.data = self.data()
        self.requested_services = self.requested_services()
        self.requested_features = self.requested_features()

    def data(self):
        with open(params_json) as f:
            data = json.load(f) 
        return data

    def requested_services(self):
        return list(find('jndiName', self.data))

    def requested_features(self):
        features = []
        for service in self.data['services']:
            features =  list (set(features) | set(service['features'])) 
            features + service['features'] 
        return features


class Server(object):
    def __init__(self):
        self.enabled_services = self.enabled_services()
        self.enabled_features = self.enabled_features()

    def enabled_services(self):
        services = []
        tree = ET.parse(server_xml)
        root = tree.getroot()
        for service in root:
            if service.get('jndiName') is not None:
                services.append(service.get('jndiName'))
        return services

    def enabled_features(self):
        features = []
        tree = ET.parse(server_xml)
        root = tree.getroot()
        for feature in root.iter('feature'):
            features.append(feature.text)
        return features

class Configure(Params, Server):
    def __init__(self):
        Params.__init__(self)
        Server.__init__(self)
        self.required_services = self.required_services()
        self.required_features = self.required_features()
        pass

    def required_features(self):
        features = list(set(self.requested_features) - set(self.enabled_features))
        return features

    def required_services(self):
        services = list(set(self.requested_services) - set(self.enabled_services))
        return services

    @prettify
    def configure_features(self):
        for feature in self.required_features:
            features = root.find('featureManager')
            ET.SubElement(features, 'feature').text = feature
            tree.write(server_xml) 


    def configure_services(self):
        fields = {'name':Jms}
        for key in fields:
            fields[key]()


class Jms:
    def __init__(self):
        self.data = self.data()
        print("Hello World!")

    def data(self):
        with open(test_json) as f:
            data = json.load(f) 
        return data

    def jms_connection_factory(self):
        if self.data['jmsConnectionFactory']:
            jcf = self.data['jmsConnectionFactory']
            jms_connection_factory = ET.SubElement(root, 'jmsConnectionFactory', attrib={
                                                                                    'jndiName': jcf['jndiName'],
                                                                                    'connectionManagerRef': jcf['connectionManagerRef']})
            ET.SubElement(jms_connection_factory, 'properties.wmqJms', attrib={
                                                                            'transportType': jcf['transportType'],
                                                                            'hostName': jcf['hostName'],
                                                                            'port': jcf['port'],
                                                                            'channel': jcf['channel'],
                                                                            'queueManager': jcf['queueManager']})                                                                                    
        else:
            pass

    def connection_manager(self):
        if self.data['connectionManager']:
            cm = self.data['connectionManager']
            ET.SubElement(root, 'connectionManager', attrib = {'id': cm['id'],'maxPoolSize': cm['maxPoolSize']})
            tree.write(server_xml)
        else:
            pass
    
    def jms_queue(self):
        if self.data['jmsQueue']:
            jmq = self.data['jmsQueue']
            jms_queue = ET.SubElement(root, 'jmsQueue', attrib={'id': jmq['id'], 'jndiName': jmq['jndiName']} )
            ET.SubElement(jms_queue, 'properties.wmqJms', attrib={'baseQueueName': jmq['baseQueueName'], 'baseQueueManagerName': jmq['baseQueueManagerName']})
            tree.write(server_xml)
        else:
            pass


class Jdbc:
    def __init__(self):
        # Check driver ref if exists ignore or add it
        pass

    def data_source (self):

        pass

    def connection_manager (self):

        pass

Configure().configure_services()




