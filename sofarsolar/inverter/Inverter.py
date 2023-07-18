import TcpProxy
import pprint
import InverterMsg
import FakeDNS
import os
import sys
import site
site.addsitedir('/usr/lib/python3.10/')
site.addsitedir('/usr/lib/python3.10/site-packages')
site.addsitedir('/usr/lib/python3.10/lib-dynload')
import MqttClient2
import logging
import json
import anyconfig


def create_callback(log, mqtt_client):
    def callback(data, src_address, src_port, dst_address, dst_port, direction):
        TcpProxy.TcpProxy.debug_callback(log, data, src_address, src_port, dst_address, dst_port, direction)
        data_len = len(data)
        if direction and 140 < data_len < 170:
            msg = InverterMsg.InverterMsg(data)
            dict = msg.dict()
            pp = pprint.PrettyPrinter()
            log.debug("[Inverter] Publishing to mqtt: %s" % pp.pformat(dict))
            mqtt_client.publish(json.dumps(dict, ensure_ascii=False))
    return callback


def load_config():
    mydir = os.path.dirname(os.path.abspath(__file__))
    ext_config_path = os.environ.get('EXT_CONFIG_PATH', None)
    config_paths = [mydir + '/config-org.ini']
    if os.path.exists(mydir + '/config/config.ini'):
        config_paths.append(mydir + '/config/config.ini')
    if ext_config_path and os.path.exists(ext_config_path):
        config_paths.append(ext_config_path)
    config = anyconfig.load(config_paths)
    return config


def main():
    config = load_config()

    logger = logging.getLogger("Inverter")
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    if config['log']['log_filename']:
        file_handler = logging.FileHandler(config['log']['log_filename'])
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.setLevel(logging.getLevelName(config['log']['log_level']))

    pp = pprint.PrettyPrinter()
    logger.debug("[Inverter] Config: %s" % pp.pformat(config))

    fake_dns = FakeDNS.FakeDNS(logger, config)
    mqtt_client = MqttClient.MqttClient(logger, config)
    tcp_proxy = TcpProxy.TcpProxy(config, logger, fake_dns, create_callback(logger, mqtt_client))
    try:
        mqtt_client.start()
        fake_dns.start()
        tcp_proxy.start()
        # time.sleep(3)
    except KeyboardInterrupt:
        tcp_proxy.close()
        fake_dns.close()
        mqtt_client.close()



