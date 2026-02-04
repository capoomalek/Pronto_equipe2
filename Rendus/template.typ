// --- 1. DÉFINITION DES COULEURS ---
#let imt-green = rgb(164, 210, 51)
#let imt-light-blue = rgb(0, 184, 222)
#let imt-dark-blue = rgb(12, 35, 64)
#let imt-gray = rgb(87, 87, 87)

// --- 2. FONCTION PRINCIPALE ---
#let project(
  title: "",
  subtitle: "",
  authors: (),
  date: "",
  group: "",
  version: "",
  encadrant: "",
  logo: none,
  body
) = {
  
  // Configuration globale
  set text(font: "New Computer Modern", size: 12pt, lang: "fr")
  set par(justify: true, leading: 0.65em, first-line-indent: 1.5em)
  set heading(numbering: "I.1.")

  // --- PAGE DE GARDE ---
  page(margin: 0cm)[
    
    // A. FORMES GÉOMÉTRIQUES (Coin haut droit)
    #let u = 2.2cm 
    
    #place(top + right, dx: -0.5cm, dy: 0.5cm)[
      // On réduit aussi la boite conteneur (ex: 11cm au lieu de 15cm) pour ne pas gêner le texte
      #box(width: 11cm, height: 11cm)[
        #place(top + right, dx: -0.5cm, dy: 0.5cm)[ // On rapproche un peu du bord (dx/dy réduits)
           // 1. Triangle Vert
           #place(top + right, polygon(fill: imt-green, (0pt, 0pt), (-3 * u, 0pt), (0pt, 3 * u)))
           // 2. Triangle Bleu Clair
           #place(top + right, dx: 0cm, dy: 3 * u, polygon(fill: imt-light-blue, (0pt, 0pt), (-2.24 * u, 0pt), (0pt, 2.24 * u)))
           // 3. Triangle Bleu Foncé
           #place(top + right, dx: 0cm, dy: 0cm, polygon(fill: imt-dark-blue, (-5.24 * u, 0pt), (-2.24 * u, 3 * u), (-5.24 * u, 3 * u)))
        ]
      ]
    ]

    // B. INFO ÉCOLE (Haut Gauche)
    #place(top + left, dx: 2.5cm, dy: 2.5cm)[
      #set text(size: 11pt, fill: black)
      #set par(leading: 0.5em, first-line-indent: 0pt)
      *IMT Atlantique* \
      Projet PRONTO – S6 2025-2026 \
      Campus de #group
    ]

    // C. BLOC CENTRAL UNIQUE (Titre, Date, Auteurs, Encadrant)
    // On place tout ce bloc à 11cm du haut
    #place(top + left, dx: 2.5cm, dy: 11cm)[
      #set par(first-line-indent: 0pt, leading: 0.6em)
      
      // 1. PRONTO
      #text(size: 38pt, weight: "bold", fill: imt-green.lighten(10%))[PRONTO]
      
      #v(2cm) 
      
      // 2. Titre
      #text(size: 24pt, weight: "bold", fill: black)[#title]
      
      #v(1em)
      
      // 3. Version et Date
      #set text(size: 12pt, weight: "regular")
      Version #version \
      Date #date
      
      #v(1.5cm) // Espace entre la date et les auteurs (ajustable)
      
      // 4. Auteurs (Aligné à gauche)
      #set text(style: "italic")
      #set par(hanging-indent: 0pt) // Pour aligner proprement la liste
      Auteurs : #authors.join(", ")
      
      #v(1cm) // Espace entre auteurs et encadrant
      
      // 5. Encadrant (Décalé vers la droite comme sur l'image)
      #align(right)[
        Encadré par : #box(fill: silver.lighten(60%), inset: (x: 3pt, y: 0pt), outset: (y: 3pt), radius: 2pt)[#encadrant]
        #h(2cm) // Petite marge à droite pour ne pas coller au bord
      ]
    ]

    // D. LOGO (Toujours en bas à gauche)
    #if logo != none {
       let logo-path = if type(logo) == str { logo } else { "imta_logo.pdf" }
       place(bottom + left, dx: 2.5cm, dy: -1.5cm, image(logo-path, width: 4cm))
    }
  ]

  // --- CONFIGURATION DES PAGES SUIVANTES ---
  set page(
    paper: "a4",
    margin: (top: 3cm, bottom: 3cm, x: 2.5cm),
    header: context {
      if counter(page).get().first() > 1 {
        set text(size: 9pt, fill: imt-gray)
        grid(
          columns: (1fr, 1fr),
          align(left, title),
          align(right, authors.join(", "))
        )
        v(-8pt)
        line(length: 100%, stroke: 0.5pt + imt-gray)
      }
    },
    footer: context {
      if counter(page).get().first() > 1 {
        set text(size: 9pt, fill: imt-gray)
        align(center, counter(page).display("1"))
      }
    }
  )

  body
}