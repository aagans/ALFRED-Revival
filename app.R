#Info & Licensing -------------------------------------------------------------


#Created by Aale J. Agans for Bowdoin College BIOL 2316 Evolution
#Licensed under the MIT License
#Copyright 2024 Aale J. Agans & Hawkwood Research Group
#Permission is hereby granted, free of charge, to any person obtaining a copy of
#this software and associated documentation files (the “Software”), to deal in
#the Software without restriction, including without limitation the rights to
#use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
#of the Software, and to permit persons to whom the Software is furnished to do
#so, subject to the following conditions: The above copyright notice and this
#permission notice shall be included in all copies or substantial portions of
#the Software.
#THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.


# Initialize Packages -----------------------------------------------------


library(shiny)
library(reactable)
library(DBI)
library(dbplyr)
library(dplyr)
library(pool)
library(RMySQL)


# Database Connection -----------------------------------------------------


#Define database pool connection
pool <- dbPool(
  drv = RMySQL::MySQL(),
  dbname = "alfred",
  host = "139.140.105.140",
  username = "clientInterface",
  password = "password"
)
onStop(function() {
  poolClose(pool)
})


# UI ----------------------------------------------------------------------


# Define UI for application that draws a histogram
ui <- fluidPage(
  # Application title
  titlePanel("Allele Frequency Database Revival Project"),

  # Sidebar with a slider input for number of bins
  tabsetPanel(
    tabPanel("Query Selection",
             sidebarLayout(
               sidebarPanel(
                 h2("Frequency Table Query"),
                 selectizeInput('geo',
                                "Geographic Region",
                                choices = c("Choose one" = "")),
                 selectizeInput('pop', "Ethnic Population", choices = NULL),
                 selectizeInput('site', "SNP Site", choices = NULL),
                 selectizeInput('locus', "SNP Locus", choices = NULL),
                 actionButton('loadTable', "Retrieve Frequency Data"),
               ),

               # Show a plot of the generated distribution
               mainPanel(reactableOutput("SNPFreqTable"),
                         uiOutput("download"))
             )),
    tabPanel("Population Info",
             sidebarLayout(
               sidebarPanel(
                 h2("Information about Populations"),
                 selectizeInput('geoInfo', 'Geographic Region', choices = NULL),
                 selectizeInput('popInfo', "Ethnic Population", choices = NULL),
                 actionButton('submitPop', "Retrieve Population Data")
               ),
               mainPanel(reactableOutput('populationInfo'),
                         reactableOutput('sampleInfo'))
             )),
    tabPanel("Comparison Selection",
             sidebarLayout(
               sidebarPanel(
                 h2("Commonly Sampled SNPs"),
                 selectizeInput('geoComp', "Geographic Regions", choices = c("Choose one" = ""), multiple = TRUE),
                 selectizeInput('popComp', "Ethnic Populations", choices = NULL, multiple = TRUE),
                 actionButton('submitComp', "Retrieve Comparison Data")
               ),
               mainPanel(reactableOutput('compData'))
             ))
  )
)


# Server ------------------------------------------------------------------


# Define server logic required to draw a histogram
server <- function(input, output, session) {
  #Initialize tables used
  pop_table <- tbl(pool, "populationtable")
  samplegroup_table <- tbl(pool, "samplegrouptable")
  samplecoverage_table <- tbl(pool, "samplecoveragetable")
  snp_table <- tbl(pool, "snptable")
  type_table <- tbl(pool, "tabletypetable")

  #Generate initial population list
  geo_list <- pop_table |>
    distinct(pick("geo_region")) |>
    collect()
  geo_list <- c("Choose one" = "", geo_list)
  updateSelectizeInput(inputId = "geo", choices = geo_list)
  updateSelectizeInput(inputId = "pop", choices = c("Choose one" = ""))
  updateSelectizeInput(inputId = "site", choices = c("Choose one" = ""))
  updateSelectizeInput(inputId = "locus", choices = c("Choose one" = ""))

  #Generates initial population info list
  updateSelectizeInput(inputId = 'geoInfo', choices = geo_list)

  #Generates initial population comparison list
  updateSelectizeInput(inputId = 'geoComp', choices = geo_list)


  #Update populations based on region selected
  retrieve_pops <- reactive({
    if (input$geo != "") {
      selected_geo <- input$geo
      pop_list <- pop_table |>
        select(population, geo_region) |>
        filter(geo_region == selected_geo) |>
        select(population) |>
        collect()
    }
  })

  observeEvent(retrieve_pops(), {
    pop_list <- c("Choose one" = "", retrieve_pops())
    updateSelectizeInput(inputId = "pop", choices = pop_list)
    updateSelectizeInput(inputId = "site", choices = c("Choose one" = ""))
    updateSelectizeInput(inputId = "locus", choices = c("Choose one" = ""))
  })

  #Update sites based on populations selected
  retrieve_snps <- reactive({
    if (input$pop != "") {
      selected_pop <- input$pop
      snp_list <- pop_table |>
        select(pop_uid, population) |>
        filter(population == selected_pop) |>
        inner_join(samplegroup_table) |>
        select(sample_uid) |>
        inner_join(samplecoverage_table) |>
        select(snp_uid) |>
        distinct(snp_uid) |>
        inner_join(snp_table) |>
        select(site_name) |>
        distinct(site_name) |>
        collect()
    }
  })

  observeEvent(retrieve_snps(), {
    snp_list <- retrieve_snps()
    if (length(snp_list) == 1) {
      snp_list <- unname(snp_list)
    }
    snp_list <- c("Choose one" = "", snp_list)
    updateSelectizeInput(inputId = "site",
                         choices = snp_list,
                         server = TRUE)
    updateSelectizeInput(inputId = "locus", choices = c("Choose one" = ""))
  })

  #Update loci based on sites selected
  retrieve_loci <- reactive({
    if (input$site != "") {
      selected_site <- input$site
      loci_list <- snp_table |>
        filter(site_name == selected_site) |>
        select(locus_name) |>
        distinct(locus_name) |>
        collect()
    }
  })

  observeEvent(retrieve_loci(), {
    loci_list <- retrieve_loci()
    if (length(loci_list) == 1) {
      loci_list <- unname(loci_list)
    }
    loci_list <- c("Choose one" = "", loci_list)
    updateSelectizeInput(inputId = "locus", choices = loci_list)
  })

  #Creates frequency table
  generate_table <- eventReactive(input$loadTable, {
    selected_snp <- input$site
    selected_locus <- input$locus
    selected_pop <- input$pop
    if (input$locus != "") {
      selected_snp_uid <- snp_table |>
        filter(site_name == selected_snp &
                 locus_name == selected_locus) |>
        head(1) |>
        distinct(pick(snp_uid)) |>
        collect() |>
        as.character()

      selected_tabletype_uid <- samplecoverage_table |>
        filter(snp_uid == selected_snp_uid) |>
        head(1) |>
        distinct(pick(tabletype_uid)) |>
        collect() |>
        as.character()

      freq_table <- type_table |>
        filter(tabletype_uid == selected_tabletype_uid) |>
        head(1) |>
        distinct(pick(type_num)) |>
        collect() |>
        as.character()

      type_table <- tbl(pool, freq_table)
      selected_pop_uid <- pop_table |>
        select(pop_uid, population) |>
        filter(population == selected_pop) |>
        head(1) |>
        distinct(pick(pop_uid)) |>
        collect() |>
        as.character()

      sample_uids <- samplegroup_table |>
        select(sample_uid, pop_uid) |>
        filter(pop_uid == selected_pop_uid) |>
        distinct(pick(sample_uid)) |>
        collapse()

      freq_table <- type_table |>
        filter(SNPCol == selected_snp_uid) |>
        inner_join(sample_uids, by = join_by(SampCol == sample_uid)) |>
        select(!SNPCol) |>
        collect() |>
        mutate(Population = selected_pop) |>
        relocate(Population, .before = SampCol) |>
        relocate("Sample ID" = SampCol)
    }
  })

  #Render table in UI
  observeEvent(generate_table(), {
    freq_table <- generate_table()
    output$SNPFreqTable <- renderReactable({
      reactable(freq_table, searchable = TRUE)
    })
    output$download <- renderUI({
      downloadButton("downloadTable")
    })
  })

  #Download frequency table
  output$downloadTable <- downloadHandler(
    filename = "allele_freq.tsv",
    content = function(file) {
      freq_table <- generate_table()
      write.table(freq_table, file, sep = "\t")
    }
  )

  #Update population info selection with populations from selected region
  retrieve_pops_info <- reactive({
    if (input$geoInfo != "") {
      selected_geoInfo <- input$geoInfo
      pop_info_list <- pop_table |>
        select(population, geo_region) |>
        filter(geo_region == selected_geoInfo) |>
        select(population) |>
        collect()
    }
  })

  observeEvent(retrieve_pops_info(), {
    pop_list <- c("Choose one" = "", retrieve_pops_info())
    updateSelectizeInput(inputId = "popInfo", choices = pop_list)
  })

  generatePopSNPTable <- eventReactive(input$submitPop, {
    if (input$popInfo != "") {
      selected_pop <- input$popInfo
      selected_pop_uid <- pop_table |>
        select(pop_uid, population) |>
        filter(population == selected_pop) |>
        distinct(pick(pop_uid)) |>
        collect() |>
        as.character()

      selected_sample_uids <- samplegroup_table |>
        filter(pop_uid == selected_pop_uid) |>
        select(sample_uid) |>
        collapse()

      sample_info_df <- samplecoverage_table |>
        inner_join(selected_sample_uids) |>
        inner_join(snp_table) |>
        select(sample_uid, site_name, locus_name) |>
        distinct() |>
        collect() |>
        group_by(site_name) |>
        summarise(sample_uid = list(sample_uid), locus_name = list(locus_name)) |>
        relocate(
          "Sample ID" = sample_uid,
          "SNP Site" = site_name,
          "Locus Name" = locus_name
        )
    }
  })
  observeEvent(generatePopSNPTable(), {
    info_table <- generatePopSNPTable()
    output$populationInfo <- renderReactable({
      reactable(info_table, searchable = TRUE)
    })
  })
  generatePopInfoTable <- eventReactive(input$submitPop, {
    if (input$popInfo != "") {
      selected_pop <- input$popInfo
      snp_list <- pop_table |>
        select(pop_uid, population) |>
        filter(population == selected_pop) |>
        inner_join(samplegroup_table) |>
        select(sample_uid, sample_size, sample_desc) |>
        distinct() |>
        collect() |>
        relocate("Sample ID" = sample_uid,
                 "Sample Size" = sample_size,
                 "Sample Description" = sample_desc)
    }
  })
  observeEvent(generatePopInfoTable(), {
    info_table <- generatePopInfoTable()
    output$sampleInfo <- renderReactable({
      reactable(info_table, searchable = TRUE)
    })
  })
  retrieve_comp_pops <- reactive({
    if (!is.null(input$geoComp)) {
      selected_geoComp <- input$geoComp
      pop_list <- pop_table |>
        select(population, geo_region) |>
        filter(geo_region %in% selected_geoComp) |>
        select(population) |>
        collect()
    }
  })
  observeEvent(retrieve_comp_pops(), {
    pop_list <- c("Choose one" = "", retrieve_comp_pops())
    updateSelectizeInput(inputId = "popComp", choices = pop_list)
  })

  generateCompPopTable <- eventReactive(input$submitComp, {
    if (!is.null(input$popComp)){
      selected_pop <- input$popComp
      selected_snp_uid <- pop_table |>
        select(pop_uid, population) |>
        filter(population %in% selected_pop) |>
        select(pop_uid) |>
        distinct(pop_uid) |>
        inner_join(samplegroup_table) |>
        select(pop_uid, sample_uid) |>
        inner_join(samplecoverage_table) |>
        inner_join(snp_table) |>
        distinct(snp_uid, pop_uid, .keep_all = TRUE) |>
        group_by(snp_uid) |>
        summarize(pop_uid = n(), site_name = site_name, locus_name = locus_name) |>
        collect() |>
        filter(pop_uid == length(selected_pop)) |>
        select(site_name, locus_name) |>
        relocate("SNP Name" = site_name, "Locus Name" = locus_name)
    }
  })
  observeEvent(generateCompPopTable(), {
    comp_table <- generateCompPopTable()
    output$compData <- renderReactable({
      reactable(comp_table, searchable = TRUE)
    })
  })
}

# Run the application
shinyApp(ui = ui, server = server)
