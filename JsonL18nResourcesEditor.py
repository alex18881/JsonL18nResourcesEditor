import sublime
import sublime_plugin
import json
import os
import fnmatch

def jsonencode(str):
	return json.dumps(str, sort_keys=False, ensure_ascii=False, indent=4, separators=(',', ': '))

class JSONSaver( sublime_plugin.EventListener ):
	def on_pre_save(self, view):
		if not view.settings().get( 'l18ion_view', False ):
			return

		win = view.window()
		views = win.views()
		keys  = []
		for indx, view_i in enumerate(views):
			selection = sublime.Region( 0, view_i.size() )
			content = view_i.substr( selection )
			lines = content.splitlines()

			if indx == 0:
				keys = lines
			elif view_i == view:
				result = {}
				for key_indx, key in enumerate(keys):
					if key_indx < len(lines) and lines[key_indx] and len(key) > 0:
						result[key] = json.loads(lines[key_indx])
				
				view_i.settings().set( "l18ion_view_content", content )
				view_i.run_command( 'l18ion_save', { "jsonresult": jsonencode(result) } )
		return False

	def on_post_save(self, view):
		if not view.settings().get( 'l18ion_view', False ) or not view.settings().has( "l18ion_view_content" ):
			return

		content = view.settings().get( "l18ion_view_content", "" )
		view.settings().erase( "l18ion_view_content" )
		view.settings().set( 'l18ion_view', True )
		view.run_command( "l18ion_restore_view", { "content": content } )

class L18ionRestoreViewCommand( sublime_plugin.TextCommand ):
	def run( self, edit, content='' ):
		selection = sublime.Region( 0, self.view.size() )
		self.view.replace( edit, selection, content )


class L18ionSaveCommand( sublime_plugin.TextCommand ):
	def run( self, edit, content='', jsonresult="" ):
		selection = sublime.Region( 0, self.view.size() )
		self.view.replace( edit, selection, jsonresult )


class L18ionSetViewPos( sublime_plugin.TextCommand ):
	def run( self, edit, currentrow=0 ):
		view = self.view
		selection = sublime.Region( 0, view.size() )
		lines = view.substr( selection ).splitlines()
		newLineCount = 1+currentrow - len(lines)

		if newLineCount > 0:
			lineContent = "" if view.settings().get( "l18ion_keysview", False ) else '""'
			lines = lines + ([lineContent] * newLineCount)
			self.view.replace( edit, selection, "\n".join(lines) )
		
		#print( currentrow )
		pt = view.text_point(currentrow,0)
		view.sel().clear()
		view.sel().add( sublime.Region(pt) )


class JsonL18nCommand(sublime_plugin.TextCommand):
	def run(self, edit, **args):
		paths = args.get('paths', None)
		if paths:
			filepaths = self.get_files(paths[0])
			if filepaths and len(filepaths) > 0:
				self.make_views(filepaths); #.insert(edit, 0, json.JSONEncoder().encode(filepaths))

	def get_files(self, basepath):
		parts = os.path.basename(basepath).split(".")
		ptrn = ""
		#str.join(iterable)
		#files = 
		if len(parts) > 1:
			ptrn = "".join([parts[0], "*.",parts[len(parts)-1]])
		else:
			ptrn = "".join([parts[0], "*."])

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

		for indx,c in enumerate(files):
			view = newwin.open_file( c )
			newwin.set_view_index( view, indx+1, 0 )


		self.get_views_contens( newwin, files )

	def get_views_contens(self, win, files):
		isloading = False
		views = win.views()

		for view in views:
			if not view.settings().get( "l18ion_keysview", False ):
				#print( str(isloading) )
				isloading = isloading or view.is_loading()

		if isloading:
			sublime.set_timeout( lambda: self.get_views_contens( win, files ), 10 )
		else:
			jsons = [ self.get_view_content(win, view_i) for view_i in views if not view_i.settings().get( "l18ion_keysview", False ) ]
			#print( json.JSONEncoder().encode(jsons) )
			keys = {};
			for dict in jsons:
				for key in dict.keys():
					keys[key] = key

			self.render_content( win, keys, keys, 0, "Keys" )

			for indx, dict in enumerate(jsons):
				self.render_content( win, keys, dict, indx+1, files[indx] )
			
			ViewSyncer( win )
				

	def get_view_content( self, win, view ):
		selection = sublime.Region( 0, view.size() )
		content = view.substr( selection )
		return json.loads( content )

	def render_content(self, win, keys, dict, indx, filePath):
		view = win.views()[indx]
		content = []

		if indx == 0:
			content = "\n".join([ str(dict.get(key, "")) for key in keys ])
		else:
			content = "\n".join([ jsonencode(dict.get(key, "")) for key in keys ])

		view.run_command( 'l18ion_restore_view', { 'content': content } )

		#view.set_name( filePath if indx == 0 else os.path.basename( filePath ) )
		view.set_viewport_position( (0, 0), False )
		view.settings().set( 'l18ion_view_file_path', filePath )
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
				view.settings().set( 'l18ion_view_prev_row', rowindx )
				
				if indx != rowViewIndex:
					view.run_command( 'l18ion_set_view_pos', { "currentrow": rowindx } )

	def sync(self):
		if not self.window:
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

			prevRow = view.settings().get( 'l18ion_view_prev_row', 1 )

			if prevRow != rowPos:
				rowindex = indx
				currrow = rowPos

			if scrollPrevPosY != scrollpos1:
				scrollindx = indx
				scrollpos = scrollpos1

		if scrollindx > -1 or rowindex > -1:
			self.update_pos( scrollindx, scrollpos, rowindex, currrow )
		
		sublime.set_timeout( self.sync, self.timeout_focused )