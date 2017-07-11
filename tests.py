#!/usr/bin/env python3

import unittest

from core.tests.test_serializer import SerializerTests  # noqa
from core.tests.test_broker import BrokerTests  # noqa
from core.tests.test_resource import ResourceTests  # noqa


if __name__ == "__main__":
    unittest.main()
