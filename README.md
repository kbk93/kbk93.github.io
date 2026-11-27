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
