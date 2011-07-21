import sublime, sublime_plugin
import os
import plistlib
from xml.etree import ElementTree
from zipfile import ZipFile

snippets = []

class Snippet:
	def __init__(self, desc, content, tab, scopes):
		self.desc = desc
		self.code = content
		self.tab = tab
		self.scopes = scopes

def parse_snippet(f, ext):
	if ext == '.sublime-snippet':
		tree = ElementTree.parse(f)

		desc = tree.find('description').text
		content = tree.find('content').text
		trigger = tree.find('tabTrigger').text
		scope = tree.find('scope').text.split(', ')

	elif ext == '.tmSnippet':
		plist = plistlib.readPlist(f)
		desc = plist['name']
		content = plist['content']
		trigger = plist['tabTrigger']
		scope = plist['scope']
	
	return Snippet(desc, content, trigger, scope)

def read_zip(path):
	results = []
	zipf = ZipFile(path, 'r')
	for name in zipf.namelist():
		ext = os.path.splitext(name)[-1]
		if ext in ('.sublime-snippet', '.tmSnippet'):
			f = zipf.open(name, 'rb')
			results.append(parse_snippet(f, ext))
			f.close()
	
	return results

def find_snippets():
	global snippets

	new_snippets = []
	# Packages folder
	for root, dirs, files in os.walk(sublime.packages_path()):
		for name in files:
			try:
				ext = os.path.splitext(name)[-1]
				if ext in ('.sublime-snippet', '.tmSnippet'):
					path = os.path.join(root, name)
					f = open(path, 'rb')
					new_snippets.append(parse_snippet(f, ext))
					f.close()
				elif ext == '.sublime-package':
					new_snippets += read_zip(path)

			except:
				pass
	
	# Installed Packages folder
	for root, dirs, files in os.walk(sublime.installed_packages_path()):
		for name in files:
			try:
				ext = os.path.splitext(name)[-1]
				if ext == '.sublime-package':
					path = os.path.join(root, name)
					new_snippets += read_zip(path)
			except:
				pass

	snippets = new_snippets

find_snippets()

class Sniptastic(sublime_plugin.TextCommand):
	def run(self, edit):
		view = self.view
		names = self.view.scope_name(self.view.sel()[0].b)
		scopes = []
		for name in names.split(' '):
			scope = []
			for section in name.split('.'):
				scope.append(section)
				scopes.append('.'.join(scope))

		candidates = []
		for s in snippets:
			for scope in s.scopes:
				if scope in scopes:
					candidates.append(s)

		items = [s.desc for s in candidates]

		def callback(idx):
			if idx == -1: return # -1 means the menu was canceled
			self.view.run_command('insert_snippet', {'contents':candidates[idx].code})

		view.window().show_quick_panel(items, callback)
