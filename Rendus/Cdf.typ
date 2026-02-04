#import "template.typ": project

#show: project.with(
  title: "Modèle de cahier des charges fonctionnel",
  subtitle: "PRONTO", // Si vous voulez l'afficher sous le titre
  authors: (
    "Équipe de pilotage PRONTO",
    "Prénom Nom",
  ),
  date: "26/01/2026",
  group: "Nantes", // Le campus (utilisé dans le bloc haut gauche)
  version: "1.1",
  encadrant: "Prénom Nom",
  logo: true, // Mettre true si le fichier "imta_logo.pdf" est présent
)
#pagebreak()

