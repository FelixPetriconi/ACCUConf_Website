from flask import render_template, jsonify, redirect, url_for, session, request
from flask import send_from_directory, g
from accuconf.models import *
from accuconf.proposals.utils.roles import Role
from accuconf.proposals.utils.proposals import *
from accuconf.proposals.utils.validator import *
import hashlib
from random import randint
from . import proposals

_proposal_static_path = None


@proposals.record
def init_blueprint(ctxt):
    app = ctxt.app
    proposals.config = app.config
    proposals.logger = app.logger
    global _proposal_static_path
    _proposal_static_path = proposals.config.get("NIKOLA_STATIC_PATH", None)
    if _proposal_static_path is None:
        message = 'NIKOLA_STATIC_PATH not set properly.'
        proposals.logger.info(message)
        raise ValueError(message)
    assert _proposal_static_path.is_dir()


@proposals.route("/")
def index():
    if proposals.config.get("MAINTENANCE"):
        return redirect(url_for("maintenance"))

    # when_where = {}
    # committee = {}
    # venuefile = proposals.config.get('VENUE')
    # committeefile = proposals.config.get('COMMITTEE')
    # if venuefile.exists():
    #     when_where = json.loads(venuefile.open().read())
    #
    # if committeefile.exists():
    #     committee = json.loads(committeefile.open().read())
    #
    # frontpage = {
    #     "title": "ACCU Conference 2017",
    #     "data": "Welcome to ACCU Conf 2017",
    #     "when_where": when_where,
    #     "committee": committee.get("members", [])
    # }
    # if 'user_id' in session:
    #     user = User.query.filter_by(user_id=session["user_id"]).first()
    #     if not user:
    #         proposals.logger.error("user_id key present in session, but no user")
    #         return redirect(url_for('proposals.logout'))
    #     else:
    #         frontpage["user_name"] = "%s %s" % (user.user_info.first_name,
    #                                             user.user_info.last_name)
    # return render_template("proposals/index.html", page=frontpage)
    return redirect(url_for('nikola.index'))


@proposals.route("/maintenance")
def maintenance():
    return render_template("maintenance.html")


@proposals.route("/login", methods = ['GET', 'POST'])
def login():
    if proposals.config.get("MAINTENANCE"):
        return redirect(url_for("maintenance"))
    if request.method == "POST":
        userid = request.form['usermail']
        passwd = request.form['password']
        user = User.query.filter_by(user_id=userid).first()
        if not user:
            return redirect(url_for('index'))
        password_hash = hashlib.sha256(passwd.encode("utf-8")).hexdigest()
        if user.user_pass == password_hash:
            session['user_id'] = user.user_id
            proposals.logger.info("Auth successful")
            g.user = userid
            return redirect(url_for("nikola.index"))
        else:
            proposals.logger.info("Auth failed")
            return redirect(url_for("proposals.login"))
    elif request.method == "GET":
        page = {"title": "Login Page"}
        return render_template("login.html", page=page)


@proposals.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@proposals.route("/register", methods=["GET", "POST"])
def register():
    if proposals.config.get("MAINTENANCE"):
        return redirect(url_for("maintenance"))
    if request.method == "POST":
        # Process registration data
        user_email = request.form["email"]
        user_pass = request.form["user_pass"]
        first_name = request.form["firstname"]
        last_name = request.form["lastname"]
        country = request.form["country"]
        state = request.form["state"]
        phone = request.form["phone"]
        postal_code = request.form["pincode"]

        encoded_pass = ""
        if type(user_pass) == str and len(user_pass):
            encoded_pass = hashlib.sha256(user_pass.encode('utf-8')).hexdigest()

        page = {}
        if not validateEmail(user_email):
            page["title"] = "Registration failed"
            page["data"] = "Registration failed: Invalid/Duplicate user id."
            page["data"] += "Please register again"
            return render_template("registration_failure.html", page=page)

        elif not validatePassword(user_pass):
            page["title"] = "Registration failed"
            page["data"] = "Registration failed: Password did not meet checks."
            page["data"] += "Please register again"
            return render_template("registration_failure.html", page=page)
        else:
            newuser = User(user_email, encoded_pass)
            userinfo = UserInfo(newuser.user_id,
                                first_name,
                                last_name,
                                phone,
                                Role.user.get("name", "user")
                                )
            userlocation = UserLocation(newuser.user_id,
                                        country,
                                        state,
                                        postal_code)
            newuser.user_info = userinfo
            newuser.location = userlocation

            db.session.add(newuser)
            db.session.add(userinfo)
            db.session.add(userlocation)
            db.session.commit()
            page["title"] = "Registration successful"
            page["data"] = "You have successfully registered for submitting "
            page["data"] += "proposals for the ACCU Conf. Please login and "
            page["data"] += "start preparing your proposal for the conference."
            return render_template("registration_success.html", page=page)
    elif request.method == "GET":
        num_a = randint(10, 99)
        num_b = randint(10, 99)
        sum = num_a + num_b
        question = MathPuzzle(sum)
        db.session.add(question)
        db.session.commit()
        register = {
            "title": "Register",
            "data": "Register here for submitting proposals to ACCU Conference",
            "question": question.id,
            "puzzle": "%d + %d" % (num_a, num_b)
        }
        return render_template("register.html", page=register)


@proposals.route("/show_proposals", methods=["GET"])
def show_proposals():
    if proposals.config.get("MAINTENANCE"):
        return redirect(url_for("maintenance"))
    if session.get("user_id", False):
        user = User.query.filter_by(user_id=session["user_id"]).first()
        if not user:
            page = {
                "name": "Submit proposal"
            }
            return render_template("not_loggedin.html", page=page)

        page = {
            "subpages": [],
        }
        for proposal in user.proposals:
            subpage = {}
            subpage["proposal"] = {
                "title": proposal.title,
                "abstract": proposal.text,
                "proposaltype": getProposalType(proposal.session_type).proposalType(),
                "presenters": proposal.presenters
            }
            page["subpages"].append(subpage)
        return render_template("view_proposal.html", page=page)
    else:
        page = {
            "name": "Submit proposal"
        }
        return render_template("not_loggedin.html", page=page)


@proposals.route("/submit_proposal", methods=["POST"])
def submit_proposal():
    if proposals.config.get("MAINTENANCE"):
        return redirect(url_for("maintenance"))
    if session.get("user_id", False):
        user = User.query.filter_by(user_id=session["user_id"]).first()
        if not user:
            page = {
                "name": "Submit proposal"
            }
            return render_template("not_loggedin.html", page=page)

        page = {
            "title": "Submit a proposal for ACCU Conference",
            "user_name": "%s %s" % (user.user_info.first_name,
                                    user.user_info.last_name),
        }
        page["proposer"] = {
            "email": user.user_id,
            "first_name": user.user_info.first_name,
            "last_name": user.user_info.last_name,
            "country": user.location.country,
            "state": user.location.state
        }
        return render_template("submit_proposal.html", page=page)
    else:
        page = {
            "name": "Submit proposal"
        }
        return render_template("not_loggedin.html", page=page)


@proposals.route("/upload_proposal", methods=["POST"])
def upload_proposal():
    if proposals.config.get("MAINTENANCE"):
        return redirect(url_for("maintenance"))

    if session.get("user_id", False):
        user = User.query.filter_by(user_id=session["user_id"]).first()
        if not user:
            page = {
                "name": "Proposal Submission"
            }
            return render_template("not_logged.html", page=page)
        else:
            proposalData = request.json
            proposals.logger.info(proposalData)
            status, message = validateProposalData(proposalData)
            response = {}
            if status:
                proposal = Proposal(proposalData.get("proposer"),
                                    proposalData.get("title"),
                                    getProposalType(proposalData.get(
                                        "proposalType")),
                                    proposalData.get("abstract"))
                user.proposals.append(proposal)
                db.session.add(proposal)
                presenters = proposalData.get("presenters")
                for presenter in presenters:
                    proposalPresenter = ProposalPresenter(proposal.id,
                                                          presenter["email"],
                                                          presenter["lead"],
                                                          presenter["fname"],
                                                          presenter["lname"],
                                                          presenter["country"],
                                                          presenter["state"])
                    proposal.presenters.append(proposalPresenter)
                    db.session.add(proposalPresenter)
                db.session.commit()
                response["success"] = True
                response["message"] = "Thank you very much!\nYou have successfully submitted a proposal for the next ACCU conference!\nYou can see it now under \"My Proposal\"."
                response["redirect"] = url_for('proposals.index')
            else:
                response["success"] = False
                response["message"] = message
            return jsonify(**response)
    else:
        page = {
            "name": "Submit proposal"
        }
        return render_template("not_loggedin.html", page=page)


@proposals.route("/review_proposal", methods=["GET"])
def review_proposal():
    if proposals.config.get("MAINTENANCE"):
        return redirect(url_for("maintenance"))
    if session.get("user_id", False):
        user = User.query.filter_by(user_id=session["user_id"]).first()
        if not user:
            page = {
                "name": "Submit proposal"
            }
            return render_template("not_loggedin.html", page=page)

        page = {
            "Title": "Review Proposal",
        }

        proposalToShowNext = None
        allProposals = Proposal.query.filter(Proposal.proposer != session["user_id"]).order_by(Proposal.id)
        allProposalsReverse = Proposal.query.filter(Proposal.proposer != session["user_id"]).order_by(Proposal.id.desc())

        if session.get("review_button_pressed", False):
            if session["review_button_pressed"] == "next_proposal":
                proposalToShowNext = findNextElement(allProposals, session["review_id"])
            elif session["review_button_pressed"] == "previous_proposal":
                proposalToShowNext = findNextElement(allProposalsReverse, session["review_id"])
        else:
            proposalToShowNext = allProposals.first()

        if not proposalToShowNext:
            page = {
                "Title": "All reviews done",
                "Data": "You have finished reviewing all proposals!",
            }
            return render_template("review_success.html", page=page)

        nextAvailable = False
        previousAvalaible = False

        if allProposals.first().id != proposalToShowNext.id:
            previousAvalaible = True
        if allProposalsReverse.first().id != proposalToShowNext.id:
            nextAvailable = True

        proposalReview = ProposalReview.query.filter_by(proposal_id=proposalToShowNext.id,
                                                        reviewer=user.user_id).first()
        proposalComment = ProposalComment.query.filter_by(proposal_id=proposalToShowNext.id,
                                                          commenter=user.user_id).first()

        page["proposal"] = {
            "title": proposalToShowNext.title,
            "abstract": proposalToShowNext.text,
            "proposaltype": getProposalType(proposalToShowNext.session_type).proposalType(),
            "presenters": proposalToShowNext.presenters,
            "score": 0,
            "comment": "",
            "next_enabled" : nextAvailable,
            "previous_enabled" : previousAvalaible,
        }

        if proposalReview:
            page["proposal"]["score"] = proposalReview.score
        if proposalComment:
            page["proposal"]["comment"] = proposalComment.comment

        session['review_id'] = proposalToShowNext.id

        return render_template("review_proposal.html", page=page)
    else:
        page = {
            "name": "Submit proposal"
        }
        return render_template("not_loggedin.html", page=page)


@proposals.route("/upload_review", methods=["POST"])
def upload_review():
    if proposals.config.get("MAINTENANCE"):
        return redirect(url_for("maintenance"))
    if session.get("user_id", False):
        user = User.query.filter_by(user_id=session["user_id"]).first()
        if not user:
            page = {
                "name": "Submit proposal"
            }
            return render_template("not_loggedin.html", page=page)

        if session.get("review_id", False):
            proposal = Proposal.query.filter_by(id=session["review_id"]).first()
            if proposal != None:
                reviewData = request.json
                proposals.logger.info(reviewData)

                proposalReview = ProposalReview.query.filter_by(proposal_id=proposal.id,
                                                                reviewer=user.user_id).first()

                if proposalReview:
                    proposalReview.score = reviewData["score"]
                    ProposalReview.query.filter_by(proposal_id=proposal.id,
                                                   reviewer=user.user_id).update({'score': proposalReview.score})
                else:
                    proposalReview = ProposalReview(proposal.id,
                                                    user.user_id,
                                                    reviewData["score"])
                    proposal.reviews.append(proposalReview)
                    db.session.add(proposalReview)

                proposalComment = ProposalComment.query.filter_by(proposal_id=proposal.id,
                                                                  commenter=user.user_id).first()
                if proposalComment:
                    proposalComment.comment = reviewData["comment"]
                    ProposalComment.query.filter_by(proposal_id=proposal.id,
                                                    commenter=user.user_id).update(
                                                        {'comment': proposalComment.comment})
                else:
                    proposalComment = ProposalComment(proposal.id,
                                                      user.user_id,
                                                      reviewData["comment"])
                    proposal.comments.append(proposalComment)
                    db.session.add(proposalComment)

                db.session.commit()
                session['review_button_pressed'] = reviewData["button"]

                response = {}
                response["success"] = True
                response["redirect"] = url_for('proposals.review_proposal')
                return jsonify(**response)
    else:
        page = {
            "name": "Submit proposal"
        }
        return render_template("not_loggedin.html", page=page)


@proposals.route("/check/<user>", methods=["GET"])
def check_duplicate(user):
    if proposals.config.get("MAINTENANCE"):
        return redirect(url_for("maintenance"))
    u = User.query.filter_by(user_id=user).first()
    result = {}
    if u:
        result["duplicate"] = True
    else:
        result["duplicate"] = False
    return jsonify(**result)


@proposals.route("/captcha/validate", methods=["POST"])
def validate_captcha():
    captchaInfo = request.json
    qid= captchaInfo.get("question_id")
    ans = captchaInfo.get("answer")
    q = MathPuzzle.query.filter_by(id=qid).first()
    result = {"valid": False}
    if q:
        if q.answer == ans:
            result["valid"] = True

    return jsonify(**result)


@proposals.route("/captcha/new", methods=["POST"])
def generate_captcha():
    captchaInfo = request.json
    result = {"valid": True}
    qid = captchaInfo.get("question_id")
    if not qid:
        result["valid"] = False
    else:
        question = MathPuzzle.query.filter_by(id=qid).first()
        if question:
            num_a = randint(10, 99)
            num_b = randint(10, 99)
            sum = num_a + num_b
            question.answer = sum
            db.session.commit()
            result["valid"] = True
            result["question"] = "%d + %d" % (num_a, num_b)
        else:
            result["valid"] = False

    return jsonify(**result)


@proposals.route('/assets/<path:path>')
def asset(path):
    proposals.logger.info("assets accessed")
    proposals.logger.info("Requested for {}".format(path))
    source_path = _proposal_static_path / 'assets'
    proposals.logger.info("Sending from: {}".format(source_path))
    return send_from_directory(source_path.as_posix(), path)


@proposals.route('/navlinks', methods=["GET"])
def navlinks():
    loggedIn = False
    loggedOut = True
    numberOfProposals = 0
    myProposalsText = ""
    if session.get("user_id", False):
        loggedIn = True
        loggedOut = False
        user = User.query.filter_by(user_id=session["user_id"]).first()
        numberOfProposals = len(user.proposals)
        canReview = user.user_info.role == "reviewer";
        if numberOfProposals==1:
            myProposalsText = "My Proposal"
        else:
            myProposalsText = "My Proposals"
    links = {
        "0": ("Home", url_for("nikola.index"), True),
        "1": ("Login", url_for("proposals.login"), loggedOut),
        "2": ("Register", url_for("proposals.register"), loggedOut),
        "3": (myProposalsText, url_for("proposals.show_proposals"), loggedIn and numberOfProposals>0),
        "4": ("Submit Proposal", url_for("proposals.submit_proposal"), loggedIn),
        "5": ("Review Proposals", url_for("proposals.review_proposal"), loggedIn and canReview),
        "6": ("RSS", "/site/rss.xml", True),
        "7": ("Log out", url_for("proposals.logout"), loggedIn)
    }

    return jsonify(**links)


@proposals.route('/currentuser', methods=["GET"])
def currentuser():
    userinfo = {}
    userinfo["user_id"] = ""
    if session.get("user_id", False):
        user = User.query.filter_by(user_id=session["user_id"]).first()
        userinfo["user_id"] = user.user_id
        userinfo["first_name"] = user.user_info.first_name
        userinfo["last_name"] = user.user_info.last_name
    return jsonify(**userinfo)

# return the next element after id
def findNextElement(list, id):
    found = False
    for it in list:
        if found:
            return it
        if it.id == id:
            found = True
    return None

def neighborhood(iterable):
    iterator = iter(iterable)
    prev_item = None
    current_item = next(iterator)  # throws StopIteration if empty.
    for next_item in iterator:
        yield (prev_item, current_item, next_item)
        prev_item = current_item
        current_item = next_item
    yield (prev_item, current_item, None)

