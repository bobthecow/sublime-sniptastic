import sublime_plugin

snippets = {
	'foo':{'code':'if ($1) {$2; $3}', 'scope':'source'},
	'bar':{'code':'class $1 extends $2 {\n\t$3\n}', 'scope':'source'}
}

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

		candidates = [snippet for snippet in snippets if snippets[snippet]['scope'] in scopes]
		def callback(idx):
			if idx == -1: return # -1 means the menu was canceled
			snippet = candidates[idx]
			self.view.run_command('insert_snippet', {'contents':snippets[snippet]['code']})

		view.window().show_quick_panel(candidates, callback)
