import unittest
import time

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

    def test_record_writes_to_endpoint(self):
        my_metrics = metrics.Metrics()
        my_metrics.sock = Mock()
        my_metrics.enabled = True
        my_metrics.record('mymetric', 1)
        self.assertTrue(my_metrics.sock.sendall.called)
