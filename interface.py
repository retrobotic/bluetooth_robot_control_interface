#! /usr/bin/python
# -*- coding:Utf-8 -*-
import os
import serial
import pygame
from pygame.locals import *
os.environ["SDL_FBDEV"] = "/dev/fb1"

# Couleurs
R = (100,150,100)# teinte1
Y = (100,200,100)# teinte2
G = (100,250,100)# teinte3
B = (100,230,80)# teinte4
P = (100,180,80)# teinte5
O = (100,130,80)# teinte6

bluetoothSerial = serial.Serial( "/dev/rfcomm1", baudrate=9600 )# Initialisation bluetooth

def print_func(arg):
	print arg



# Liste des données pour les touches du clavier
KEYS = [
	#couleur
	#| texte
	#|   |   textes niveau 2 (même ordre que dans la liste principale)
	#v   v   ou tuples (texte, fonction)
	################# BUG A CORRIGER ############################
	(R, "Robot",["HOME","test","g + r","b + r",("Auto ON",lambda: bluetoothSerial.write("autoon")),"o + r"]),
	(Y, "None",[("Avancer",lambda: bluetoothSerial.write("avancer")),"HOME","g + y","b + y",("",lambda: bluetoothSerial.write("i")),"o + y"]),
	(G, "None",[("Stop",lambda: bluetoothSerial.write("stop")),"test","HOME","b + g",("Lumieres ON",lambda: bluetoothSerial.write("elumiereon)),"o + g"]),
	(B, "None",[("Gauche",lambda: bluetoothSerial.write("gauche")),("teeest",lambda: print_func("Double O !")),"g + b","HOME",("Auto OFF",lambda: bluetoothSerial.write("autooff")),"o + b"]),
	(P, "Func Robot",[("Reculer",lambda: bluetoothSerial.write("reculer")),"y + p","g + p","b + p","HOME","o + p"]),
	(O, "None",[("Droite",lambda: bluetoothSerial.write("droite")),"y + o","g + o","b + o",("Lumieres OFF",lambda: bluetoothSerial.write("lumiereoff")),"HOME"])]
	############### BUG A CORRIGER ###############################

# Taille du clavier
WIDTH = 320
HEIGHT = 240

# Format de la grille
ROWS = 2
COLUMNS = 3


def create_keys(surf):
	"""Renvoie la liste des touches, créées à partir des données initiales
 
	surf : pygame.Surface
        surface d'affichage des touches
	"""
	keys_list = []

	# Position de la case courante sur la grille
	column = 0
	row = 0

	# Taille de chaque case; chaque touche fait cette taille moins deux pixels
	# de chaque côté
	w = WIDTH / COLUMNS
	h = HEIGHT / ROWS

	for value, (color, text, level_2) in enumerate(KEYS):
		rect = pygame.Rect(column * w, row * h, w, h)

		# Traitement de la liste de données des clés et transformation en
		# dictionnaire
		l_2 = {}
		for i, v in enumerate(level_2):
			if isinstance(v, (str, bytes)):
				l_2[i] = (v, lambda t=v: print_func(t))
			else:
				l_2[i] = v

		keys_list.append( Key(surf, rect.inflate(-2, -2), color, text, value, l_2))

		column += 1
		row += column // COLUMNS
		column %= COLUMNS

	return keys_list

def apply_brightness(color, delta=10):
	"""Renvoie une nouvelle couleur dont la luminosité a été changée

	`delta` doit se situer entre -100 (plus sombre) et 100 (plus lumineux)
	"""
	if isinstance(color, pygame.Color):
		new = pygame.Color(color.r, color.g, color.b, color.a)

	elif isinstance(color, (tuple, list)):
		new = pygame.Color(*color)

	else:
		new = pygame.Color(color)

	h, s, l, a = new.hsla
	new.hsla = (h, s, max(min(int(l + delta), 100), 0), a)

	return new

class Key:
	"""Objet représentant une touche du clavier virtuel
	"""
	def __init__(self, surf, rect, color, text, value, level_2={}):
		"""Constructeur de l'objet Key()
		surf : pygame.Surface
			surface où dessiner la touche

		rect : pygame.Rect
			rectangle délimitant la touche

		color : pygame.Color
			couleur propre de la touche

		text : str
			texte affiché sur la touche au niveau 1

		value : object
			valeur de la touche, utilisée dans le second niveau
			Chaque touche du clavier doit avoir une valeur différente.

		level_2={} : {object: [str, callable]}
			données de la touche pour le niveau 2

			Chaque clé du dictionnaire correspond à la valeur de la touche
			cliquée au niveau 1; lui est associé une liste contenant une chaîne
			de caractères qui sera affichée sur la touche (son nom) et la
			fonction à appeler si le clic est relâché sur la touche courante.
		"""
		self.surf = surf
		self.rect = rect
		self.color = color
		self.text = text
		self.value = value
		self.level_2 = level_2

		# Si une touche niveau 1 est enfoncée, la touche enfoncée sera assignée
		# à l'attribut suivant, qui permet de savoir la couleur et la valeur
		# de la touche enfoncée.
		# Si aucune touche n'est enfoncée, l'attribut revient à None.
		self.down = None

		# Présence de la souris au-dessus de la touche
		self.has_focus = False

	def __bool__(self):
		"""Renvoie le booléen caractérisant la touche; ce sera toujours `True`
		"""
		return True

	def draw(self):
		"""Redessine la touche en prenant en compte l'éventuelle touche enfoncée

		La fonction n'appelle pas pygame.display.flip()
		"""
		if not self.down:
			color = self.color
			text = self.text
			rect = self.rect

		else:
			color = self.down.color
			value = self.down.value

			if value in self.level_2.keys():
				text = self.level_2[value][0]

			else:
				text = ""

			if self.down is self:
				rect = self.rect.inflate(2, 2).clamp(self.surf.get_rect())

			else:
				rect = self.rect

		if self.has_focus:
			color = apply_brightness(color, 10)

		# On colore la touche
		self.surf.fill(color, rect)

		# On crée et on "blitte" le texte de la touche
		text_surf = FONT.render(text, True, (30, 30, 30))
		self.surf.blit(text_surf, text_surf.get_rect(center=self.rect.center))

	def set_level_2(self, key):
		"""Met la touche au niveau 2 lorsqu'une touche a été cliquée
		key : Key
		touche cliquée au niveau 1
		"""
		self.down = key
		self.draw()

	def end_level_2(self):
		"""Ramène la touche au niveau 1
		"""
		self.down = False
		self.draw()

	def set_focus(self):
		"""Indique que la souris est sur la touche, et la met en surbrillance
		Renvoie True si l'écran doit être rafraîchi
		"""
		if not self.has_focus:
			self.has_focus = True
			return True
		else:
			return False

	def release_focus(self):
		"""Indique que la souris n'est plus sur la touche
		Renvoie True si l'écran doit être rafraîchi
		"""
		if self.has_focus:
			self.has_focus = False
			return True
		else:
			return False

	def run_command(self):
		"""Lance la fonction associée à la touche de niveau 2
		"""
		if self.down.value in self.level_2.keys():
			func = self.level_2[self.down.value][1]
			func()


class Keyboard:
	"""Objet représentant le clavier virtuel ; il est composé de plusieurs Key()
	"""
	def __init__(self, surf, keys):
		"""Constructeur de l'objet Keyboard()
		surf : pygame.Surface
			surface d'affichage du clavier
			keys : [Key, ...]
			liste des touches du clavier
		"""
		self.surf = surf
		self.keys = keys

		# Touche de niveau 1 pressée
		self.pressed = None

		self.keep_level_2 = False

		self.draw()

	def click(self, coord):
		"""Fonction appelée lorsqu'on clique sur le clavier
		coord : (int, int)
		coordonnées du clic
		"""
		# Recherche du bouton cliqué
		for k in self.keys:
			if k.rect.collidepoint(coord):
				self.pressed = k

				# Passage de toutes les touches au niveau 2
				for kk in self.keys:
					kk.set_level_2(k)
				break

		self.draw()

	def release(self, coord):
		"""Fonction appelée lorsque le clic est relâché

		coord : (int, int)
			coordonnées du relâchement
		"""
		if self.pressed:
			# Recherche du bouton où a lieu le relâchement
			for k in self.keys:
				if k.rect.collidepoint(coord):
					if k is self.pressed:
						if self.keep_level_2:
							self.pressed = None
							for kk in self.keys:
								kk.end_level_2()

						self.keep_level_2 = not self.keep_level_2

						self.draw()
						return

					# Exécution de l'action rattachée à la touche
					else:
						k.run_command()
					break

			if not self.keep_level_2:
				# Passage de toutes les touches au niveau 1
				for kk in self.keys:
					kk.end_level_2()

				self.pressed = None

		self.draw()

	def draw(self):
		"""Redessine le clavier
		"""
		self.surf.fill((50,50,50))#Couleur du fond

		for k in self.keys:
			if k is not self.pressed:
				k.draw()

		# On dessine en dernier l'éventuelle touche pressée
		if isinstance(self.pressed, Key):
			self.pressed.draw()

		pygame.display.flip()

	def update_focus(self, coord):
		"""Met en surbrillance la touche sous le curseur

		coord : (int, int)
			position du curseur
		"""
		# Indique si l'écran doit être redessiné
		refresh = False
		for k in self.keys:
			if k.rect.collidepoint(coord):
				refresh |= k.set_focus()

			else:
				refresh |= k.release_focus()

		if refresh:
			self.draw()

	def run(self):
		"""Lance la boucle principale pour gérer les événements
		"""
		while True:
			event = pygame.event.wait()

			if event.type == MOUSEBUTTONDOWN and event.button == 1 and not self.keep_level_2:
				self.click(event.pos)

			elif event.type == MOUSEBUTTONUP and event.button == 1:
				self.release(event.pos)

			if event.type == MOUSEMOTION:
				self.update_focus(event.pos)

			elif event.type == QUIT:
				pygame.display.quit()
				exit()

if __name__ == '__main__':
	pygame.init()

	FONT = pygame.font.SysFont("arial", 14, True)#Police de caractere

	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	keys = create_keys(screen)
	kb = Keyboard(screen, keys)
	kb.run()