library(rjson)
library(stringr)
library(ggplot2)
library(alphashape3d)
setwd("~/rens2")

#
# 3D TOP results 
#

# Get all files in a list
file.list <- list.files("output/")
file.list <- file.list[grep("3D_top_results.txt",file.list)]

# Open one file to get dimensions
tmp <- fromJSON(file=paste0(c("output/",file.list[1]),collapse = ""))
trait.list <- NULL
for (i in 1:length(tmp$observations)){
  trait.list <- c(trait.list,rep(tmp$observations[[i]]$trait,1))
}
trait.list <- c("sample_name", trait.list)

# Create dataframe for observations
pheno.collect <- data.frame(matrix(NA,nrow = 0,ncol = length(trait.list)), stringsAsFactors = FALSE)
colnames(pheno.collect) <- trait.list
# Now loop over the data and insert values into the dataframe
for ( j in 1:length(file.list[1:4])){
  tmp <- fromJSON(file=paste0(c("output/",file.list[j]),collapse = ""))
  pheno.tmp <- data.frame(file.list[j], ncol = length(trait.list), nrow = 1, stringsAsFactors = FALSE)
  pheno.vector <- c(file.list[j])
  for (i in 1:length(tmp$observations)){ # Loop over values and add them to vector
    pheno.tmp <- cbind(pheno.tmp, tmp$observations[[i]]$value[1])
    pheno.vector <- c(pheno.vector, tmp$observations[[i]]$value[1])
  }
  # Add new observation here
  #pheno.tmp <- data.frame(pheno.tmp, stringsAsFactors = FALSE)
  pheno.vector <- data.frame(pheno.vector, stringsAsFactors = FALSE)
  colnames(pheno.tmp) <- trait.list
  pheno.collect <- rbind(pheno.collect, pheno.tmp[1,]) # For some reason pheno.tmp has two rows, so only use the first one
}

#
# 3D Volume thingy
#

punten <- read.csv("~/rens2/input/0030_2018-03-14 14.21 - 238A_0_3D.csv", header=FALSE)
x <- cbind(punten[,1], punten[,2], punten[,3])
ashape3d.obj <- ashape3d(x, alpha = 1, pert = TRUE)
components_ashape3d(ashape3d.obj, 1)
plot(ashape3d.obj, byComponents = TRUE)
volume_ashape3d(ashape3d.obj, byComponents = FALSE, indexAlpha = 'all')
