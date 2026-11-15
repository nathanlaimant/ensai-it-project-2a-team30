// =====================================================================
// Global Setup
// =====================================================================
#let global_styles(body) = {
  show link: set text(fill: rgb("#1a73e8"))  
  
  show heading: it => {
    block(above: 2em, below: 1em, it)
  }

  set bibliography(title: [*Bibliographie*], full: false)

  body
}

// =====================================================================
// Cover page
// =====================================================================
#let cover_page(title:[], team:[], authors:[], teacher: [], tutor: [], project: [], logo_path: "img/ensai_logo.png") = {
  align(horizon + center)[
    #image(logo_path, width: 65%)
    #v(3em)
    #line(start: (0cm, 0cm), end: (17cm, 0%), stroke: (thickness: 2pt))
    #text(size: 24pt, weight: "bold", title)\
    #line(start: (0cm, 0cm), end: (17cm, 0%), stroke: (thickness: 2pt))
    #v(1em)
    #text(size: 14pt, team)
    #v(2em)
  ]

  grid(
    columns: (1fr, 1fr),
    align: (left, right),
    [
      *Étudiants :* \
      #authors.map(a => [#a]).join("\n")
    ],
    [
      *Responsable :* \
      #teacher\
      *Tuteur :*\
      #tutor
    ]
  )

  align(bottom + center)[
    #v(5em)
    #text(project)
  ]
}

// =====================================================================
// Template
// =====================================================================
#let project_template(
  title: [], team: [], authors: [], teacher: [], tutor: [], project: [], 
  logo_path: "img/ensai_logo.png",
  body 
) = {
  show: global_styles

  set page(footer: none)

  cover_page(
    title: title, team: team, authors: authors, 
    teacher: teacher, tutor: tutor, project: project, logo_path: logo_path
  )

  // Table of contents
  pagebreak()
  set page(fill: none, margin: auto)
  align(horizon, outline(indent: auto, title: [Table des matières]))

  // Page numbering begins after the table of contents
  pagebreak()
  counter(page).update(1)
  set page(footer: context { set align(center); counter(page).display() })

  body
}