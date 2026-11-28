# Ben Khalifa's

Site statique de Karim et Mehdi Ben Khalifa.

Le site est généré par `python3 build/build.py` à partir de `build/data/`.

## Publier depuis le téléphone

La page privée `/admin/` (non liée au menu, non indexée) permet d'ajouter des
images dans Arts ou dans un thème de caricatures. Elle redimensionne l'image sur
le téléphone, puis envoie en un seul commit : l'image et sa miniature dans
`uploads/`, `build/data/galleries.json` et les pages de galerie mises à jour.
Elle s'ouvre avec une clé GitHub (fine-grained, accès « Contents : Read and
write » sur ce dépôt uniquement), gardée chiffrée sur le téléphone avec un mot
de passe.

## Articles (Blog et و الحمد لله)

Dans `/admin/`, l'onglet « Article » publie un article dans le Blog ou dans la
page و الحمد لله (`/alhamdulillah/`). Le texte s'écrit simplement : ligne vide
pour un nouveau paragraphe, `## ` pour un titre de partie, `> ` pour une
citation ou un verset, `- ` pour une liste, `**gras**`, `*italique*`,
`[texte](https://lien)`. L'arabe s'affiche de droite à gauche tout seul.

Les articles sont dans `build/data/posts.json` (champ `section` : `blog` ou
`deen`), leur texte dans `build/data/posts/<slug>.html` (et `.md` pour ceux
écrits depuis l'admin). `build/build.py` écrit aussi `build/data/shell.json`,
le modèle de page que l'admin remplit pour créer un article sans lancer Python.
