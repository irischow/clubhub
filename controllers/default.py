# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

from gluon.tools import Crud


def index():
	"""
	example action using the internationalization operator T and flash
	rendered by views/default/index.html or views/generic.html

	if you need a simple wiki simply replace the two lines below with:
	return auth.wiki()
	"""
	# response.flash = T("Hello World")
	return dict()

@auth.requires_login()
def clubs():
	if auth.has_membership('admin'):
		if request.args(0) is None:
			form = Crud(db).create(db.club)
		else:
			form = Crud(db).update(db.club, request.args(0))
	else:
		form = None

	if request.vars.has_key('cmd'):
		for key in request.vars.keys():
			if key.startswith('check'):
				club_id = key[5:]
				db.club_member.insert(member_id=auth.user, club=club_id)

	belongs_to = [row.club for row in db(db.club_member.member_id==auth.user).select(db.club_member.ALL)]

	return dict(clubs=db(db.club).select(orderby=db.club.name), belongs_to=belongs_to, form=form)

@auth.requires_login()
def my_clubs():
	if auth.has_membership('admin'):
		if request.args(0) is None:
			form = Crud(db).create(db.club)
		else:
			form = Crud(db).update(db.club, request.args(0))
	else:
		form = None

	if request.vars.has_key('cmd'):
		for key in request.vars.keys():
			if key.startswith('check'):
				club_id = key[5:]
				db.club_member.insert(member_id=auth.user, club=club_id)

	sort = request.vars.get('sort', 'name')
	if sort == 'day':
		order = db.day_number.day_number | db.club.name
	else:
		order = db.club.name

	belongs_to = [row.club for row in db(db.club_member.member_id==auth.user).select(db.club_member.ALL)]
	clubs = db(db.club.id > 0).select(left = db.day_number.on(db.day_number.day_name == db.club.meeting_day),
			orderby = order)
	return dict(form = form, clubs = clubs, belongs_to = belongs_to, sort = sort)

@auth.requires_login()
def club():
	club_id = request.args(0)

	crud = Crud(db)
	crud.settings.update_deletable = False
	if auth.has_membership('admin') or is_president(club_id):
		form = crud.update(db.club, club_id)
	else:
		form = None

	if request.vars.has_key('cmd'):
		for key in request.vars.keys():
			if key.startswith('check'):
				member_id = key[5:]
				db((db.club_member.member_id == member_id) & (db.club_member.club == club_id)).update(president=True)


	club = db.club(db.club.id==club_id)
	members = db(db.club_member.club == club_id).select(
			left = db.auth_user.on(db.auth_user.id == db.club_member.member_id),
			orderby=~db.club_member.president|db.auth_user.last_name|db.auth_user.first_name)
	return dict(club=club, form=form, members=members)

@auth.requires_membership('admin')
def add_member():
	if request.vars.has_key('add'):
		count = db((db.club_member.member_id == request.vars.member) & (db.club_member.club == request.vars.club)).count()
		if count == 0:
			data = dict(member_id=request.vars.member, club=request.vars.club, president=request.vars.has_key('president'))
			db.club_member.insert(**data)
			response.flash = 'Member added.'
		else:
			row = db(db.auth_user.id==request.vars.member).select().first()
			member_name = row.first_name + ' ' + row.last_name
			row = db(db.club.id==request.vars.club).select().first()
			club_name = row.name
			response.flash = '%s already a member of %s.' % (member_name, club_name)

	clubs = db(db.club).select(orderby=db.club.name)
	members = db(db.auth_user).select(orderby=db.auth_user.last_name|db.auth_user.first_name)
	return dict(clubs=clubs, members=members)

def about_us():
	return dict()

def contact_us():
	return dict()

def is_president(club_id):
	row=db((db.club_member.club==club_id) & (db.club_member.member_id==auth.user)).select(db.club_member.ALL).first()
	return row.president is True if row else False

def download():
	return response.downlad(request, db)

def user():
	"""
	exposes:
	http://..../[app]/default/user/login
	http://..../[app]/default/user/logout
	http://..../[app]/default/user/register
	http://..../[app]/default/user/profile
	http://..../[app]/default/user/retrieve_password
	http://..../[app]/default/user/change_password
	http://..../[app]/default/user/bulk_register
	use @auth.requires_login()
		@auth.requires_membership('group name')
		@auth.requires_permission('read','table name',record_id)
	to decorate functions that need access control
	also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
	"""
	return dict(form=auth())


@cache.action()
def download():
	"""
	allows downloading of uploaded files
	http://..../[app]/default/download/[filename]
	"""
	return response.download(request, db)


def call():
	"""
	exposes services. for example:
	http://..../[app]/default/call/jsonrpc
	decorate with @services.jsonrpc the functions to expose
	supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
	"""
	return service()
