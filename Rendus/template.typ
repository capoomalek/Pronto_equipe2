// --- COULEURS IMT ATLANTIQUE ---
#let imt-green = rgb(164, 210, 51)
#let imt-light-blue = rgb(0, 184, 222)
#let imt-dark-blue = rgb(12, 35, 64)
#let imt-gray = rgb(87, 87, 87)

// --- FONCTION PRINCIPALE DU TEMPLATE ---
#let project(
  title: "",
  subtitle: "",
  authors: (),
  date: "",
  promo: "",
  group: "",
  version: "",
  logo: none,
  body
) = {
  
  // 1. Configuration globale
  set text(font: "Times New Roman", size: 12pt, lang: "fr")
  set par(justify: true, leading: 0.65em, first-line-indent: 1.5em)
  
  
  // Numérotation des sections (I.1.) - Seul réglage conservé pour les titres
  set heading(numbering: "I.1.")

  // 2. PAGE DE GARDE
  page(margin: (top: 0cm, bottom: 0cm, left: 0cm, right: 0cm))[
    
    // --- LES TRIANGLES ---
    // Ajout du décalage dx/dy pour créer la marge blanche demandée
    #let u = 2.5cm 
    
    #place(top + right, dx: -1cm, dy: 1cm)[ 
      #box(width: 15cm, height: 15cm)[
        // 1. Triangle Vert (Coin haut droit)
        #place(top + right, polygon(
          fill: imt-green,
          (0pt, 0pt), (-3 * u, 0pt), (0pt, 3 * u)
        ))

        // 2. Triangle Bleu Clair (Sous le vert)
        #place(top + right, dx: 0cm, dy: 3 * u, polygon(
          fill: imt-light-blue,
          (0pt, 0pt), (-2.24 * u, 0pt), (0pt, 2.24 * u)
        ))

        // 3. Triangle Bleu Foncé (À gauche)
        #place(top + right, dx: 0cm, dy: 0cm, polygon(
          fill: imt-dark-blue,
          (-5.24 * u, 0pt), (-2.24 * u, 3 * u), (-5.24 * u, 3 * u)
        ))
      ]
    ]

    // --- LE TEXTE (Aligné gauche) ---
    #place(top + left, dx: 2.5cm, dy: 9cm)[
      #set text(font: "Arial", size: 11pt, fill: black)
      #set par(leading: 0.6em, justify: false, first-line-indent: 0pt)
      
      // Date
      #date
      #v(0.5em)
      
      // Auteurs
      #authors.join(" - ")
      #v(1.5em)

      // Infos Groupe / Promo
      #grid(
        columns: (auto, auto),
        gutter: 3cm,
        [Demi-Promo #promo],
        [Equipe #group]
      )

      #v(2cm)

      // Titre (Vert, Gros, Gras)
      #text(font: "Arial", weight: "bold", size: 24pt, fill: imt-green, title)
      
      #v(0.2em)
      
      // Sous-titre (Vert, Moyen)
      #text(font: "Arial", size: 14pt, fill: imt-green, subtitle)
    ]

    // --- LE LOGO (Bas Gauche) ---
    #place(bottom + left, dx: 2.5cm, dy: -2.5cm)[
      #if logo != none {
        image("imta_logo.pdf", width: 5cm)
      }
    ]
  ]

  // 3. Configuration des pages suivantes
  set page(
    paper: "a4",
    margin: (top: 3cm, bottom: 3cm, x: 2.5cm),
    header: context {
      if counter(page).get().first() > 1 {
        set text(font: "Arial", size: 9pt, fill: imt-gray)
        grid(
          columns: (1fr, 1fr),
          align(left, title),
          align(right, authors.join(", "))
        )
        line(length: 100%, stroke: 0.5pt + imt-gray)
      }
    },
    footer: context {
      if counter(page).get().first() > 1 {
        set text(font: "Arial", size: 9pt, fill: imt-gray)
        align(center, counter(page).display("1"))
      }
    }
  )

  body
}