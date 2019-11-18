#' ---
#'  
#' # Introductie
#' 
#' Planten bestaan enzo

#'  
#' # Beschrijvende statistiek
#'  

#' De dataset ziet er als volgt uit
#' 
library(rjson)
library(stringr)

#' setting workdirectory
setwd("C:/Users/RensD/OneDrive/studie/Master/The_big_project/output")
top_files <- Sys.glob("*top_results.txt")
lijstje <- rep(NA, length(top_files))
i <- 1
for(file in top_files){
  resultsfile <- fromJSON(file = file)
  data <- resultsfile$observations
  GT <- str_extract(file, "- [0-9]*_cam")
  GT <- substring(GT, 3, 4)
  data$GT <- GT
  append(lijstje, data, after = i)
  i <- i + 1
}

print(data$GT)
#do.call(rbind, Map(data.frame, A = data, B=data))


#frame <- data.frame("number", "genotype", "observations")




