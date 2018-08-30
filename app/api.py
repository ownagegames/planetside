import websocket, json, requests

pApiKey = "ownage"

def apiQuery(_type, _arg):
	if (_type == "getOutfit"):
		_req = requests.get('https://census.daybreakgames.com/s:{}/get/ps2/outfit/?alias_lower={}&c:resolve=leader(faction_id),member_character(name)'.format(_apikey, _arg.lower()))
		_req_data = json.loads(_req.text)
		for p in _req_data['outfit_list']:
			_outfit_name = p.get('name')
			_outfit_tag = p.get('alias')
			_outfit_id = p.get('outfit_id')
			_faction_id = p.get('leader', {}).get('faction_id')
			_data = {'outfit_details':[], 'members':[]}
			_json_string = {'outfit_name':'{}'.format(_outfit_name), 'outfit_tag':'{}'.format(_outfit_tag), 'outfit_id':'{}'.format(_outfit_id), 'outfit_faction':'{}'.format(_faction_id)}
			_data.get('outfit_details').append(_json_string)
		for m in p['members']:
			_char_id = m.get('character_id')
			_char_name = m.get('name', {}).get('first')
			_json_string = {'character_id':'{}'.format(_char_id),'character_name':'{}'.format(_char_name)}
			_data.get('members').append(_json_string)
		return json.dumps(_data)
	if (_type == "getWeapon"):
		_req = requests.get('https://census.daybreakgames.com/s:{}/get/ps2/item?item_id={}&c:show=item_category_id,name,item_type_id&c:lang=en'.format(_apikey, _arg))
		_req_data = json.loads(_req.text)
		return _req_data

def subscribeKillfeed(_players, _timer, _match_id, db):
	def ws_open(ws):
		ws.send('{{"service":"event","action":"subscribe","characters":[{}],"eventNames":["Death"]}}'.format(_players[:-1]))
		startTimer(_timer, _match_id)
	def ws_close(ws):
		insertStop = db.session.query(matches).filter_by(match_id=_match_id).first()
		insertStop.match_status = "Stopped"
		db.session.commit()
	def ws_error(ws, error):
		print (error)
	def ws_message(ws, message):
		_data = json.loads(message)
		print (json.dumps(_data))

		matchD = db.session.query(matches).filter_by(match_id=_match_id).first()
		if (matchD.match_timer != '0'):
			a_id = jsonSearch(_data, ['payload', 'attacker_character_id'])
			a_class = jsonSearch(_data, ['payload', 'attacker_loadout_id'])
			a_weapon = jsonSearch(_data, ['payload', 'attacker_weapon_id'])
			is_headshot = jsonSearch(_data, ['payload', 'is_headshot'])
			b_id = jsonSearch(_data, ['payload', 'character_id'])
			b_class = jsonSearch(_data, ['payload', 'character_loadout_id'])
			if (a_id == 'None'):
				pass
			else:
				updateScore(_match_id, a_id, a_weapon, a_class, b_id, b_class, is_headshot)
		else:
			ws.send('{{"service":"event","action":"clearSubscribe","characters":[{}],"eventNames":["Death"]}}'.format(_players[:-1]))
			ws.close()
	websocket.enableTrace(True)
	ws = websocket.WebSocketApp("wss://push.planetside2.com/streaming?environment=ps2&service-id=s:{}".format(_apikey), on_open = ws_open, on_message = ws_message, on_error = ws_error, on_close=ws_close)
	ws.run_forever()