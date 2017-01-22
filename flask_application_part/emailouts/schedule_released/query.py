from accuconf.models import Proposal
from accuconf.proposals.utils.proposals import ProposalState


def query():
    proposals = Proposal.query.filter_by(status=ProposalState.acknowledged)

    def uniquify(proposer, presenters):
        return {proposer} | {pp for pp in (p.presenter for p in presenters) if pp.email != proposer.email}

    return tuple((None, person) for proposal in proposals for person in uniquify(proposal.proposer, proposal.presenters))


def edit_template(text_file, proposal, person):
    with open(text_file) as tf:
        return tf.read().strip()
