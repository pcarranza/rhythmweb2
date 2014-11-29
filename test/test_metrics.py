import unittest
import time
import socket

from mock import Mock, patch
from rhythmweb import metrics

class MetricsBasicTest(unittest.TestCase):

    def test_basic_measurement(self):
        @metrics.time('my_metric')
        def fake_function(value):
            time.sleep(0.1)
            return 'returning {}'.format(value)
    
        with patch('rhythmweb.metrics.metrics') as metrics_mock:
            return_value = fake_function('fake')
            self.assertEquals('returning fake', return_value)
            metric, timed = metrics_mock.record.call_args[0]
            self.assertEquals(metric, 'my_metric')
            self.assertTrue(0.1 < timed)


class MetricsSetupTest(unittest.TestCase):

    def test_when_disabled_record_does_not_write_to_endpoint(self):
        my_metrics = metrics.Metrics()
        my_metrics.sock = Mock()
        my_metrics.enabled = False
        my_metrics.record('mymetric', 1)
        self.assertFalse(my_metrics.sock.sendall.called)

    def test_when_enabled_socket_is_connected_and_is_called(self):
        with patch('rhythmweb.metrics.socket') as sock:
            my_sock = Mock()
            sock.socket.return_value = my_sock
            my_metrics = metrics.Metrics()
            my_metrics.enabled = True
            my_metrics.record('mymetric', 1)
            sock.socket.assert_called_with()
            my_sock.connect.assert_called_with(('127.0.0.1', 2003))
            call_args = my_sock.sendall.call_args_list[0][0]
            self.assertEquals('rhythmweb.mymetric', call_args[0].decode('utf8').split()[0])

    def test_when_enabled_and_socket_fails_connection_exception_is_logged(self):
        with patch('rhythmweb.metrics.socket') as sock, patch('rhythmweb.metrics.log') as log:
            e = socket.error('Just because')
            sock.socket.side_effect = e
            my_metrics = metrics.Metrics()
            my_metrics.enabled = True
            my_metrics.record('mymetric', 1)
            log.exception.assert_called_with('Could not open metrics socket %s', e)

    def test_when_enabled_and_socket_fails_sending_exception_is_logged(self):
        with patch('rhythmweb.metrics.log') as log:
            e = socket.error('Just because')
            my_metrics = metrics.Metrics()
            my_metrics.sock = Mock()
            my_metrics.sock.sendall.side_effect = e
            my_metrics.enabled = True
            my_metrics.record('mymetric', 1)
            log.exception.assert_called_with('Could not send metrics %s: %s', 'mymetric', e)
