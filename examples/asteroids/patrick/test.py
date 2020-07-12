
def listener():

	print("start")

	while True:
		symbol, modifiers = yield "on_key_press"
		print("key_press", symbol, modifiers)


class Window():

	def __init__(self):
		self.listeners = {}

	def add_listener(self, f)
		gen = f()
		listen_for = next(gen)
		if listen_for not in self.listeners:
			self.listeners[listen_for] = []

		self.listeners[listen_for].append(gen)


	def dispatch_event(event_name, *args):

		if event_name not in self.listeners: return

		for gen in self.listeners[event_name]:
			new_event = gen.send(*args)


x = Window()
x.on_key_press("W","asdf")
x.on_key_press("A","asdf")
x.on_key_press("S","asdf")