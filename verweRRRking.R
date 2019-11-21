library(rjson)
library(stringr)

## load one file

setwd("~/studie/master/data")
tmp <- fromJSON(file="output_lab/0200_2018-03-07 08.55 - 26_cam9top_results.txt")
tmp

## test see what is in data file
tmp$observations$horizontal_reference_position
tmp$observations$height_above_reference
tmp$observations$hue_circular_mean
tmp$observations$green_frequencies
tmp$observations$solidity$value
tmp$observations[[1]]$value
length(tmp$observations)

## make trait list 
trait.list <- NULL
for (i in 1:length(tmp$observations)){
  trait.list <- c(trait.list,rep(tmp$observations[[i]]$trait,length(tmp$observations[[i]]$value)))
                  }
trait.list

## get data
file.list <- list.files("output_lab/")
file.list <- file.list[grep("results.txt",file.list)]
file.list

pheno.collect <- matrix(NA,nrow = length(file.list),ncol = length(trait.list))
for ( j in 1:length(file.list)){
tmp <- fromJSON(file=paste0(c("output_lab/",file.list[j]),collapse = ""))
pheno.tmp <- NULL
GT <- str_extract(file.list[j], "- [0-9]*_cam")
GT <- substring(GT, 3, 4)
for (i in 1:length(tmp$observations)){
  pheno.tmp <- c(pheno.tmp,tmp$observations[[i]]$value)
}
pheno.collect[j,] <- pheno.tmp
}
colnames(pheno.collect) <- trait.list
rownames(pheno.collect) <- file.list
pheno.collect[1:5,1:5]

pheno.collect <- data.frame(pheno.collect)
plot(pheno.collect$area.above.reference)
plot(pheno.collect$solidity)

