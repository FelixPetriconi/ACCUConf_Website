'''
Tests for submitting a proposal.
'''

import json

import pytest

from common import client, get_and_check_content, post_and_check_content

from accuconf.models import User, Proposal

__author__ = 'Balachandran Sivakumar, Russel Winder'
__copyright__ = '© 2016  Balachandran Sivakumar, Russel Winder'
__licence__ = 'GPLv3'


@pytest.fixture(scope='function')
def registration_data():
    return {
        'email': 'a@b.c',
        'user_pass': 'Password1',
        'firstname': 'User',
        'lastname': 'Name',
        'phone': '+011234567890',
        'pincode': '123456',
        'country': 'India',
        'state': 'TamilNadu',
        'captcha': '1',
        'question': '12',
    }


@pytest.fixture(scope='function')
def proposal_single_presenter():
    return {
        'proposer': 'a@b.c',
        'title': 'ACCU Proposal',
        'proposalType': 'quick',
        'abstract': '''This is a test proposal that will have
dummy data. Also this is not a very
lengthy proposal''',
        'presenters': [
            {
                'email': 'a@b.c',
                'lead': 1,
                'fname': 'User',
                'lname': 'Name',
                'country': 'India',
                'state': 'TamilNadu'
            },
        ]
    }


@pytest.fixture(scope='function')
def proposal_multiple_presenters_single_lead():
    return {
        'proposer': 'a@b.c',
        'title': 'ACCU Proposal',
        'proposalType': 'miniworkshop',
        'abstract': ''' This is a test proposal that will have
dummy data. Also this is not a very
lengthy proposal''',
        'presenters': [
            {
                'email': 'a@b.c',
                'lead': 1,
                'fname': 'User',
                'lname': 'Name',
                'country': 'India',
                'state': 'TamilNadu'
            },
            {
                'email': 'p2@b.c',
                'lead': 0,
                'fname': 'Presenter',
                'lname': 'Second',
                'country': 'India',
                'state': 'TamilNadu'
            },
        ]
    }


@pytest.fixture(scope='function')
def proposal_multiple_presenters_and_leads():
    return {
        'proposer': 'a@b.c',
        'title': 'ACCU Proposal',
        'proposalType': 'workshop',
        'abstract': ''' This is a test proposal that will have
dummy data. Also this is not a very
lengthy proposal''',
        'presenters': [
            {
                'email': 'a@b.c',
                'lead': 1,
                'fname': 'User',
                'lname': 'Name',
                'country': 'India',
                'state': 'TamilNadu'
            },
            {
                'email': 'p2@b.c',
                'lead': 1,
                'fname': 'Presenter',
                'lname': 'Second',
                'country': 'India',
                'state': 'TamilNadu'
            },
        ]
    }


def test_user_can_register(client, registration_data):
    post_and_check_content(client, '/proposals/register', registration_data, values=('You have successfully registered',))


def test_user_cannot_register_twice(client, registration_data):
    test_user_can_register(client, registration_data)
    post_and_check_content(client, '/proposals/register', registration_data, values=('Registration failed',))


def test_registered_user_can_login(client, registration_data):
    test_user_can_register(client, registration_data)
    post_and_check_content(client, '/proposals/login', {'usermail': registration_data['email'], 'password': registration_data['user_pass']}, code=302, values=('Redirecting',))
    get_and_check_content(client, '/site/index.html', values=('ACCU Conference',))
    # TODO How to check in the above that the left-side menu now has the proposals links?


def test_logged_in_user_can_get_submission_page(client, registration_data):
    test_registered_user_can_login(client, registration_data)
    get_and_check_content(client, '/proposals/proposal', values=('Submit a proposal',))


def test_logged_in_user_can_submit_a_single_presenter_proposal(client, registration_data, proposal_single_presenter):
    test_registered_user_can_login(client, registration_data)
    # TODO Why do we have to send JSON here but just used dictionaries previously?
    rvd = post_and_check_content(client, '/proposals/proposal/submit', json.dumps(proposal_single_presenter), 'application/json', values=('success',))
    response = json.loads(rvd)
    assert response['success']
    proposal = Proposal.query.filter_by(proposer='a@b.c').first()
    assert proposal is not None
    # TODO test stuff.
    user = User.query.filter_by(user_id='a@b.c').first()
    assert user is not None
    assert user.proposal is not None
    p = user.proposal
    assert p.proposer == user.user_id
    assert len(p.presenters) == 1
    assert proposal.session_type == 'quick'


def test_logged_in_user_can_submit_multipresenter_single_lead_proposal(client, registration_data, proposal_multiple_presenters_single_lead):
    test_registered_user_can_login(client, registration_data)
    # TODO Why do we have to send JSON here but just used dictionaries previously?
    rvd = post_and_check_content(client, '/proposals/proposal/submit', json.dumps(proposal_multiple_presenters_single_lead), 'application/json', values=('success',))
    response = json.loads(rvd)
    assert response['success']
    proposal = Proposal.query.filter_by(proposer='a@b.c').first()
    assert proposal is not None
    # TODO test stuff.
    user = User.query.filter_by(user_id='a@b.c').first()
    assert user is not None
    assert user.proposal is not None
    p = user.proposal
    assert p.proposer == user.user_id
    assert len(p.presenters) == 2
    assert proposal.session_type == 'miniworkshop'


def test_logged_in_user_user_can_submit_multipresenter_multilead_proposal(client, registration_data, proposal_multiple_presenters_and_leads):
    test_registered_user_can_login(client, registration_data)
    # TODO Why do we have to send JSON here but just used dictionaries previously?
    rvd = post_and_check_content(client, '/proposals/proposal/submit', json.dumps(proposal_multiple_presenters_and_leads), 'application/json', values=('success',))
    response = json.loads(rvd)
    assert response["success"] is False
    assert "message" in response
    assert "both marked as lead presenters" in response["message"]
    #proposal = Proposal.query.filter_by(proposer="p2@b.c").first()
    #assert proposal is not None
    # TODO test stuff.
    user = User.query.filter_by(user_id="a@b.c").first()
    assert user is not None
    assert user.proposal is None
    #p = user.proposal
    #assert p.proposer == user.user_id
    #assert len(p.presenters) == 2
