#!/usr/bin/env python

import json
from flask import render_template, jsonify, redirect, url_for, session, request
# from flask import Blueprint
from accuconf.models import *
from accuconf.proposals.utils.roles import Role
from accuconf.proposals.utils.proposals import *
from accuconf.proposals.utils.validator import *
import hashlib
from random import randint
from . import proposals


@proposals.record
def init_blueprint(ctxt):
    app = ctxt.app
    proposals.config = app.config
    proposals.logger = app.logger


@proposals.route("/")
def index():
    if proposals.config.get("MAINTENANCE"):
        return redirect(url_for("maintenance"))
    when_where = {}
    committee = {}
    venuefile = proposals.config.get('VENUE')
    committeefile = proposals.config.get('COMMITTEE')
    if venuefile.exists():
        when_where = json.loads(venuefile.open().read())

    if committeefile.exists():
        committee = json.loads(committeefile.open().read())

    frontpage = {
        "title": "ACCU Conference 2017",
        "data": "Welcome to ACCU Conf 2017",
        "when_where": when_where,
        "committee": committee.get("members", [])
    }
    if 'user_id' in session:
        user = User.query.filter_by(user_id=session["user_id"]).first()
        if not user:
            proposals.logger.error("user_id key present in session, but no user")
            return redirect(url_for('proposals.logout'))
        else:
            frontpage["user_name"] = "%s %s" % (user.user_info.first_name,
                                                user.user_info.last_name)
    return render_template("proposals/index.html", page=frontpage)


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
            return redirect(url_for("index"))
        else:
            proposals.logger.info("Auth failed")
            return redirect(url_for("proposals.login"))
    else:
        return redirect(url_for("index"))


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
        salutation = request.form["salutation"]
        suffix = request.form["suffix"]
        first_name = request.form["firstname"]
        last_name = request.form["lastname"]
        country = request.form["country"]
        state = request.form["state"]
        #states = request.form["states"]
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
                                salutation,
                                first_name,
                                last_name,
                                suffix,
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
        sum =  num_a + num_b
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


@proposals.route("/proposal")
def propose():
    if proposals.config.get("MAINTENANCE"):
        return redirect(url_for("maintenance"))
    if session.get("user_id", False):
        user = User.query.filter_by(user_id=session["user_id"]).first()
        if not user:
            return redirect(url_for('proposals.logout'))
        page = {
            "title": "Submit a proposal for ACCU Conference",
            "user_name": "%s %s" % (user.user_info.first_name,
                                    user.user_info.last_name),
        }
        if user.proposal:
            page["proposal"] = {
                "title": user.proposal.title,
                "abstract": user.proposal.text,
                "type": "Quick",
                "presenters": user.proposal.presenters
            }
            return render_template("view_proposal.html", page=page)
        else:
            page["proposer"] = {
                "email": user.user_id,
                "first_name": user.user_info.first_name,
                "last_name": user.user_info.last_name,
                "country": user.location.country,
                "state": user.location.state
            }
            return render_template("submit_proposal.html", page=page)
    else:
        return redirect(url_for('proposals.logout'))


@proposals.route("/proposal/submit", methods=["POST"])
def submit_proposal():
    if proposals.config.get("MAINTENANCE"):
        return redirect(url_for("maintenance"))

    if session.get("user_id", False):
        user = User.query.filter_by(user_id=session["user_id"]).first()
        if not user:
            return redirect(url_for('proposals.logout'))
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
                presenters = []
                response["success"] = True,
                response["redirect"] = url_for('index')
            else:
                response["success"] = False
                response["message"] = message
            return jsonify(**response)
    else:
        return redirect(url_for('proposals.logout'))


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
