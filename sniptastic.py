import sublime, sublime_plugin
import os
from xml.etree import ElementTree

snippets = []

class Snippet:
	def __init__(self, desc, content, tab, scopes):
		self.desc = desc
		self.code = content
		self.tab = tab
		self.scopes = scopes

def find_snippets():
	global snippets

	new_snippets = []
	for root, dirs, files in os.walk(sublime.packages_path()):
		for name in files:
			try:
				ext = os.path.splitext(name)[-1]
				if ext == '.sublime-snippet':
					path = os.path.join(root, name)
					tree = ElementTree.parse(path)

					description = tree.find('description').text
					content = tree.find('content').text
					tabTrigger = tree.find('tabTrigger').text
					scope = tree.find('scope').text.split(', ')

					new_snippets.append(Snippet(description, content, tabTrigger, scope))
			except:
				pass

	snippets = new_snippets

find_snippets()

class Sniptastic(sublime_plugin.TextCommand):
	def run(self, edit):
		view = self.view
		view.run_command('single_selection')
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

		print candidates, len(snippets)
		def callback(idx):
			if idx == -1: return # -1 means the menu was canceled
			self.view.run_command('insert_snippet', {'contents':candidates[idx].code})

		view.window().show_quick_panel(items, callback)
