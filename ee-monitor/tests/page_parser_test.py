from .context import page_parser


def test_retrieveDataRemaining_personal():

    file = open("tests/test-data/test_personal_bandwidth_page.txt")
    assert page_parser.retrieveDataRemaining(file.read()) == 20.1


def test_retrieveDaysRemaining_personal():

    file = open("tests/test-data/test_personal_bandwidth_page.txt")
    assert page_parser.retrieveDaysRemaining(file.read()) == 9


def test_retrieveDataRemaining_business():

    file = open("tests/test-data/test_business_bandwidth_page.txt")
    assert page_parser.retrieveDataRemaining(file.read()) == 34.8


def test_retrieveDaysRemaining_business():

    file = open("tests/test-data/test_business_bandwidth_page.txt")
    assert page_parser.retrieveDaysRemaining(file.read()) == 27
