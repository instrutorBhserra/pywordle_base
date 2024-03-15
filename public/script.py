# App frontEnd
## Imports
from js import document, window, navigator, XMLHttpRequest
from pyodide import create_proxy
import unicodedata
from routes import path_api

## Global variables
norm_word = "" # Normalized word

## Functions
### Help functions
def fix_encoding(text):
	nfkd_form = unicodedata.normalize('NFKD', text)
	norm = nfkd_form.encode('ASCII', 'ignore')
	ans = norm.decode('utf8')
	return ans.upper()

### Calculation functions
def set_green(entry, correct):
	return  [ '🟩' if e==c else '⬛' for e,c in zip(entry, correct)]

def set_yellow(entry, correct, r):
	tmp = [c for e,c in zip(entry, correct) if e!=c]
	for i,l in enumerate(entry):
		if l != correct[i] and l in tmp:
			tmp.remove(l)
			r[i]='🟨'
	return r

def calc_colors(entry, correct):
	r = set_green(entry, correct)
	return set_yellow( entry, correct, r)

def square_to_class(sqr):
	if sqr == '🟩':
		return 'bg-green'
	if sqr == '🟨':
		return 'bg-yellow'
	return 'bg-black'

### Browser functions
#### Game functions
def row_check(row, word):
	size = len(word)
	entry = get_entry(row)
	ans = calc_colors(entry, word)
	mark_answer(row,ans) # Put it before to fill the msg
	if ans == ['🟩']  * size:
		show_win_screen()
	else:
		add_row(size)
		disable_row(row)

### Direct Browser functions
#### Api
def get_word(path):
	search = window.location.search

	api = path + search
	try:
		req = XMLHttpRequest.new()
		req.open("GET",api, False)
		req.send(None)
		output = str(req.response)
	except:
		output = "erros"

	return output.upper()

#### Win screen functions
def setup_win_screen(word):
	h2 = document.querySelector("#winScreen h2")
	h2.innerText = word.upper()

	btnCopy = document.getElementById("btnCopy")
	add_py_listener(btnCopy, 'click', copy)

	winMsg = document.getElementById("winMsg")
	winMsg.innerHTML += "<br>\n<a href='%s'>%s</a>" % (*[window.location.href]*2,)

def show_win_screen(): # TODO: Attach word on start
	ms = document.getElementById("mainStack")
	winScreen = document.getElementById("winScreen")

	ms.classList.add('hidden')
	winScreen.classList.remove('hidden')

#### Template functions
def clone_template(id):
	tplt = document.getElementById(id)
	clone = tplt.content.cloneNode(True)
	child = clone.querySelector(':first-child')
	return clone, child

def create_input():
	clone , el = clone_template('inputTemplate')
	add_py_listener(el, 'input', on_input)
	add_py_listener(el,'keydown',on_key_down)
	return clone

def create_ans_btn():
	clone , el = clone_template('btnTemplate')
	add_py_listener(el, 'click',check_answer )
	return clone

#### Dom manipulation
def disable_row(row):
	for i in row.children:
		i.disabled = 'true'

def get_entry(row):
	return [i.value for i in row.getElementsByTagName('input')]

def mark_answer(row, answer):
	winMsg = document.getElementById("winMsg")
	inputs = row.getElementsByTagName('input')
	winMsg.innerHTML += '<br>\n'
	for inp, char in zip(inputs,answer):
		inp.classList.add(square_to_class(char))
		winMsg.innerHTML+=char

def create_row(word_len):
	row = document.createElement('div')
	row.classList.add('entryRow')

	for i in range(word_len):
		row.append(create_input())

	row.append(create_ans_btn())

	return row

def add_row(word_len):
	stack = document.getElementById('mainStack')

	row = create_row(word_len)
	stack.append(row)

	row.querySelector("input").focus()


#### Pre proxies
def check_answer(e):
	global norm_word
	row_check(e.target.parentElement, norm_word)

def copy(_):
	winMsg = document.getElementById("winMsg")
	navigator.clipboard.writeText(winMsg.innerText)

def on_input(event):
	if event.inputType == 'insertText' or event.inputType == 'insertCompositionText':
		event.target.value = event.data[-1].upper()
		nextEl = event.target.nextElementSibling
		nextEl.focus()

def on_key_down(event):
	if event.key.upper() == "BACKSPACE":
		event.target.value = ''
		event.target.previousElementSibling.focus()

#### Event functions
def add_py_listener(el, event,  func):
	proxy = create_proxy(func)
	el.addEventListener(event, proxy)

## System functions
def init():
	global norm_word
	word = get_word(path_api) # It is in another file

	setup_win_screen(word)
	add_row(len(word))

	norm_word = fix_encoding(word)

def main():
	init()

## Run
if __name__ == '__main__':
	main()
