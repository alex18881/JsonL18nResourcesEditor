import sublime
import sublime_plugin
import json
import re
import os
import fnmatch
from collections import OrderedDict

def jsonencode(str):
	return json.dumps(str, sort_keys=False, ensure_ascii=False, indent=4, separators=(',', ': '))

def get_settings():
	return sublime.load_settings( 'JsonL18nResourcesEditor.sublime-settings' )

def get_view_content(view):
	selection = sublime.Region( 0, view.size() )
	return view.substr( selection )

def get_view_origin_obj(view, orderedJSON):
	str = get_view_content(view)
	view.settings().set("l18ion_origin_object", str)
	return orderedJSON.decode(str)

class JSONSaver( sublime_plugin.EventListener ):
	def on_pre_save(self, view):
		if not view.settings().get( 'l18ion_view', False ):
			return

		win = view.window()
		views = win.views()
		keys  = []
		orderedJSON = json.JSONDecoder(object_pairs_hook=OrderedDict)

		for indx, view_i in enumerate(views):
			content = get_view_content( view_i )
			lines = content.splitlines()

			if view_i.settings().get( "l18ion_keysview", False ):
				keys = lines
			elif view_i == view:
				result = orderedJSON.decode(view_i.settings().get( "l18ion_origin_object", "\{\}"))

				for key in list(result):
					if key not in keys:
						del result[key]

				for key_indx, key in enumerate(keys):
					if key_indx < len(lines) and lines[key_indx] and len(key) > 0:
						result[key] = json.loads(lines[key_indx])
						#result[key] = json.loads('"' + lines[key_indx] + '"')
				
				view_i.settings().set( "l18ion_view_content", content )
				view_i.run_command( 'l18ion_save', { "jsonresult": jsonencode(result) } )
		return False

	def on_post_save(self, view):
		if not view.settings().get( 'l18ion_view', False ) or not view.settings().has( "l18ion_view_content" ):
			return

		content = view.settings().get( "l18ion_view_content", "" )
		view.settings().erase( "l18ion_view_content" )
		view.settings().set( 'l18ion_view', True )
		view.run_command( "l18ion_set_view_content", { "content": content } )

class L18ionSetViewContent( sublime_plugin.TextCommand ):
	def run( self, edit, content='' ):
		selection = sublime.Region( 0, self.view.size() )
		self.view.replace( edit, selection, content )


class L18ionSave( sublime_plugin.TextCommand ):
	def run( self, edit, content='', jsonresult="" ):
		selection = sublime.Region( 0, self.view.size() )
		self.view.replace( edit, selection, jsonresult )

class L18ionVoid( sublime_plugin.TextCommand ):
	def run( self, edit ):
		return

class L18ionInsetRow( sublime_plugin.TextCommand ):
	def run( self, edit, index=0, iscurrent=False ):
		if not self.view.settings().get( 'l18ion_view', False ):
			return

		#isKey = self.view.settings().get( "l18ion_keysview", False )

		endOfLine = self.view.line(self.view.text_point(index,0)).end()
		self.view.insert( edit, endOfLine, "\n")

class L18nUpdateRow( sublime_plugin.TextCommand ):
	def run( self, edit, value="" ):
		view = self.view
		view.replace( edit, view.line(view.sel()[0].begin()), jsonencode( value ) )


class L18ionViewExec( sublime_plugin.TextCommand ):
	def run( self, edit, **args ):
		if not self.view.settings().get( 'l18ion_view', False ):
			return

		cmd = args.get( "cmd", None )

		if not cmd:
			return

		if cmd == "tab":
			self.switch_tab( args.get('direction', None) )
		elif cmd == "open_multiline_editor":
			self.open_ml_editor( edit )
		elif cmd == "add_row":
			self.add_row( edit )
		elif cmd == "check_backspace":
			self.check_delete( edit, 1, 0, "left_delete" )
		elif cmd == "check_del":
			self.check_delete( edit, 0, 1, "right_delete" )

#TODO: finish adding rows in the middle
	def add_row( self, edit ):
		rowPos = self.view.rowcol(self.view.sel()[0].begin())[0]
		#self.view.settings().get( 'l18ion_view_active_row', rowPos )
		views = self.view.window().views()

		for view_i in views:
			view_i.run_command( "l18ion_inset_row", { "index": rowPos, "iscurrent": self.view == view_i } )


	def switch_tab(self, dir):
		if not dir:
			return

		win = self.view.window()
		viewindx = win.get_view_index(self.view)
		
		if viewindx == -1 or viewindx[0] == -1 or viewindx[1] == -1:
			return

		nextindx = viewindx[0] + (1 if dir=="right" else -1);
		
		if nextindx >= 0 and nextindx < len(win.views()):
			for view in win.views():
				if win.get_view_index(view)[0] == nextindx:
					win.focus_view( view )
					colPos = view.rowcol(view.sel()[0].begin())[1]

					if colPos == 0 and not view.settings().get( 'l18ion_keysview', False ):
						view.run_command( 'move', {"by": "characters", "forward": True} )


	def check_delete(self, edit, left_offset, right_offset, default_action):
		currPos = self.view.sel()[0].begin()
		rowStart = self.view.line(currPos).begin()
		colPos = self.view.rowcol(currPos)[1]
		colPosAbs = rowStart + colPos
		rowEnd = self.view.line(currPos).end() - right_offset
		#print( "colPos=" + str(colPos) + "; rowEnd=" + str(rowEnd) )

		if self.view.settings().get( 'l18ion_keysview', False ):
			if (left_offset == 1 and colPos > 0) or (right_offset == 1 and colPosAbs <= rowEnd):
				self.view.run_command( default_action )
		else:
			if colPos > left_offset and colPosAbs < rowEnd:
				self.view.run_command( default_action )


#TODO: finish editing multiline rows
	def open_ml_editor(self, edit):
		view = self.view
		text = view.substr( view.line(view.sel()[0].begin()) )
		view.window().show_input_panel( "", json.loads( text ), lambda nw: self.on_ml_done( edit, nw ), self.on_ml_change, self.on_ml_cancel )

	def on_ml_done(self, edit, newVal):
		self.view.run_command( "l18n_update_row", { "value": newVal } )
		#print( newVal )

	def on_ml_change(self, newVal):
		print( newVal )

	def on_ml_cancel( self ):
		print( "ML editor cancelled" )


class L18ionSetViewPos( sublime_plugin.TextCommand ):
	def run( self, edit, currentrow=0 ):
		view = self.view
		selection = sublime.Region( 0, view.size() )
		lines = view.substr( selection ).splitlines()
		newLineCount = 1+currentrow - len(lines)

		# if newLineCount > 0:
		# 	lineContent = "" if view.settings().get( "l18ion_keysview", False ) else '""'
		# 	lines = lines + ([lineContent] * newLineCount)
		# 	self.view.replace( edit, selection, "\n".join(lines) )
		
		#print( currentrow )
		pt = view.text_point(currentrow,0)
		view.sel().clear()
		view.sel().add( sublime.Region(pt) )

#TODO: Findout how to make files editable
class JsonL18nCommand(sublime_plugin.TextCommand):
	
	def run(self, edit, **args):
		paths = args.get('paths', None)

		if not paths and self.view:
			if self.view.file_name():
				paths = [ self.view.file_name() ]
			elif self.view.name():
				paths = [ self.view.name() ]

		#print( paths )
		if paths and len( paths ) > 0:
			filepaths = self.get_files(paths[0])
			if filepaths and len(filepaths) > 0:
				self.make_views(filepaths); #.insert(edit, 0, json.JSONEncoder().encode(filepaths))

	def get_files(self, basepath):
		parts = os.path.basename(basepath).split(".")
		ptrn = ""
		#str.join(iterable)
		#files = 
		ptrn = get_settings().get("resources_pattern", "").format( basename=parts[0], ext= "" if len(parts) <= 1 else parts[len(parts)-1])
		#print( ptrn )
		if ptrn:
			dirpath = os.path.dirname(basepath)
			return [os.path.join( dirpath, p ) for p in fnmatch.filter(os.listdir(dirpath), ptrn)]
		return []

	def make_views(self, files):
		count = len(files)+1
		sublime.run_command("new_window")
		newwin  = sublime.active_window()

		newwin.run_command( 'toggle_side_bar' )
		newwin.run_command( 'toggle_menu' )
		newwin.run_command( 'toggle_minimap' )

		cols = [ i/100 for i in range(0 , 101,  round(100/count)) ]
		colscount = len(cols)-1
		cells = [ [indx, 0, indx+1, 1] for indx, cell in enumerate(cols) if indx < colscount ]

		#print( str(count) + " " + json.JSONEncoder().encode(files)+ " " + json.JSONEncoder().encode(cols) + " " + json.JSONEncoder().encode(cells))

		newwin.set_layout( { "cols": cols, "rows": [0.0, 1.0], "cells": cells } )

		view = newwin.new_file( )
		view.settings().set( "l18ion_keysview", True )
		newwin.set_view_index( view, 0, 0 )

		for indx, file_path in enumerate(files):
			view = newwin.open_file( file_path )
			newwin.set_view_index( view, indx+1, 0 )


		self.make_view_content( newwin, files )

	def make_view_content(self, win, files):
		isloading = False
		views = win.views()

		for view in views:
			if not view.settings().get( "l18ion_keysview", False ):
				#print( str(isloading) )
				isloading = isloading or view.is_loading()

		if isloading:
			sublime.set_timeout( lambda: self.make_view_content( win, files ), 10 )
		else:
			orderedJSON = json.JSONDecoder(object_pairs_hook=OrderedDict)
			jsons = [ get_view_origin_obj(view_i, orderedJSON) for view_i in views if not view_i.settings().get( "l18ion_keysview", False ) ]
			#print( json.JSONEncoder().encode(jsons) )
			keysDict = OrderedDict();
			for dict in jsons:
				for key in dict.keys():
					keysDict[key] = key

			keys = sorted(keysDict.keys())

			self.render_content( win, keys, keysDict, 0, "Keys" )

			for indx, dict in enumerate(jsons):
				self.render_content( win, keys, dict, indx+1, files[indx] )
			
			ViewSyncer( win )

	def render_content(self, win, keys, dict, indx, filePath):
		view = win.views()[indx]
		content = []

		if indx == 0:
			content = "\n".join([ str(dict.get(key, "")) for key in keys ])
		else:
			content = "\n".join([ jsonencode(dict.get(key, "")) for key in keys ])

		view.run_command( 'l18ion_set_view_content', { 'content': content } )

		#view.set_name( filePath if indx == 0 else os.path.basename( filePath ) )
		view.set_viewport_position( (0, 0), False )
		#view.settings().set( 'l18ion_view_file_path', filePath )
		view.settings().set( 'l18ion_view', True )
		view.set_scratch( True )
		return view
		
class ViewSyncer( object ):
	def __init__( self, window ):
		self.window = window
		self.timeout_focused = 10
		self.timeout_unfocused = 50
		
		self.sync()
		
	def update_pos( self, lastUpdatedIndx, position, rowViewIndex, rowindx ):
		for indx, view in enumerate(self.window.views()):
			if lastUpdatedIndx > -1:
				view.settings().set( 'l18ion_view_prev_scroll', position )

				if indx != lastUpdatedIndx:
					view.set_viewport_position( (0.0,position), False )

			if rowViewIndex > -1:
				view.settings().set( 'l18ion_view_active_row', rowindx )
				
				if indx != rowViewIndex:
					view.run_command( 'l18ion_set_view_pos', { "currentrow": rowindx } )

	def sync(self):
		if not self.window or not sublime:
			return
		
		if self.window.id() != sublime.active_window().id():
			sublime.set_timeout( self.sync, self.timeout_unfocused )
			return
		
		scrollindx = -1
		rowindex = -1
		currrow = 0
		scrollpos = (0,0)
		views = self.window.views()

		for indx, view in enumerate( views ):
			scrollpos1 = view.viewport_position()[1]
			rowPos = view.rowcol(view.sel()[0].begin())[0]

			scrollPrevPosY = view.settings().get( 'l18ion_view_prev_scroll', 1 )

			prevRow = view.settings().get( 'l18ion_view_active_row', 1 )

			if prevRow != rowPos:
				rowindex = indx
				currrow = rowPos

			if scrollPrevPosY != scrollpos1:
				scrollindx = indx
				scrollpos = scrollpos1

		if scrollindx > -1 or rowindex > -1:
			self.update_pos( scrollindx, scrollpos, rowindex, currrow )
		
		sublime.set_timeout( self.sync, self.timeout_focused )