# IMPORTS
import logging

from flask import Blueprint, render_template, request, flash, redirect, url_for
from app import db, logger
from models import Draw, User, decrypt
from flask_login import current_user

# CONFIG
lottery_blueprint = Blueprint('lottery', __name__, template_folder='templates')


# VIEWS
# view lottery page
@lottery_blueprint.route('/lottery')
def lottery():
    if current_user.is_anonymous:
        logger.warning("SECURITY - Invalid access attempt [%s, %s] accessing /lottery", "ANONYMOUS", request.remote_addr)
        return redirect(url_for("users.login"))

    user = User.query.filter_by(id=current_user.id).first()
    if user.role != "user":
        logger.warning("SECURITY - Invalid access attempt [%s, %s, %s, %s] accessing /lottery", user.id, user.email,
                       user.role, request.remote_addr)
        return render_template("403.html")

    return render_template('lottery/lottery.html')


@lottery_blueprint.route('/add_draw', methods=['POST'])
def add_draw():
    submitted_draw = ''
    for i in range(6):
        submitted_draw += request.form.get('no' + str(i + 1)) + ' '
    submitted_draw.strip()

    lottery_round = 1
    current_winning_draw = Draw.query.filter_by(master_draw=True).first()
    # if a current winning draw exists
    if current_winning_draw:
        # update lottery round by 1
        lottery_round = current_winning_draw.lottery_round + 1

    # create a new draw with the form data.
    new_draw = Draw(current_user.id, numbers=submitted_draw, master_draw=False, lottery_round=lottery_round)

    # add the new draw to the database
    db.session.add(new_draw)
    db.session.commit()

    # re-render lottery.page
    flash('Draw %s submitted.' % submitted_draw)
    return lottery()


# view all draws that have not been played
@lottery_blueprint.route('/view_draws', methods=['POST'])
def view_draws():
    # get all draws that have not been played [played=0]
    playable_draws = Draw.query.filter_by(been_played=False, user_id=current_user.id).all()

    # if playable draws exist
    if len(playable_draws) != 0:
        for draw in playable_draws:
            draw.numbers = decrypt(draw.numbers, User.query.filter_by(id=draw.user_id).first().key)

        # re-render lottery page with playable draws
        redirect(url_for("lottery.lottery"))
        return render_template('lottery/lottery.html', playable_draws=playable_draws)
    else:
        flash('No playable draws.')
        return lottery()


# view lottery results
@lottery_blueprint.route('/check_draws', methods=['POST'])
def check_draws():
    if current_user.is_anonymous:
        return redirect(url_for("users.login"))

    # get played draws
    played_draws = Draw.query.filter_by(been_played=True, user_id=current_user.id).all()

    # if played draws exist
    if len(played_draws) != 0:
        for draw in played_draws:
            draw.numbers = decrypt(draw.numbers, User.query.filter_by(id=draw.user_id).first().key)

        return render_template('lottery/lottery.html', results=played_draws, played=True)

    # if no played draws exist [all draw entries have been played therefore wait for next lottery round]
    else:
        flash("Next round of lottery yet to play. Check you have playable draws.")
        return lottery()


# delete all played draws
@lottery_blueprint.route('/play_again', methods=['POST'])
def play_again():
    Draw.query.filter_by(been_played=True, master_draw=False).delete(synchronize_session=False)
    db.session.commit()

    flash("All played draws deleted.")
    return lottery()


