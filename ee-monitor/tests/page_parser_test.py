from .context import page_parser


def test_retrieveDataRemaining_personal():

    file = open("tests/test-data/test_personal_bandwidth_page.txt")
    assert page_parser.retrieveDataRemaining(file.read()) == 46.6


def test_retrieveDaysRemaining_personal():

    file = open("tests/test-data/test_personal_bandwidth_page.txt")
    assert page_parser.retrieveDaysRemaining(file.read()) == 17


def test_retrieveDataRemaining_business():

    file = open("tests/test-data/test_business_bandwidth_page.txt")
    assert page_parser.retrieveDataRemaining(file.read()) == 18.4


def test_retrieveDaysRemaining_business():

    file = open("tests/test-data/test_business_bandwidth_page.txt")
    assert page_parser.retrieveDaysRemaining(file.read()) == 0
