library(rjson)
library(stringr)
library(ggplot2)

## Load data
setwd("~/studie/master/data/")

## get data
file.list <- list.files("output_lab/")
file.list <- file.list[grep("results.txt",file.list)]

## Load data home pc
setwd("C:/Users/Rens Dijkhuizen/OneDrive/studie/Master/The_big_project")
file.list <- list.files("output_lab/")
file.list <- file.list[grep("results.txt",file.list)]

## open one temp file
tmp <- fromJSON(file=paste0(c("output_lab/",file.list[1]),collapse = ""))

trait.list <- NULL
for (i in 1:length(tmp$observations)){
  trait.list <- c(trait.list,rep(tmp$observations[[i]]$trait,length(tmp$observations[[i]]$value)))
}
tmp$observations$genotype$value


pheno.collect <- matrix(NA,nrow = length(file.list),ncol = length(trait.list))
for ( j in 1:length(file.list)){
tmp <- fromJSON(file=paste0(c("output_lab/",file.list[j]),collapse = ""))
pheno.tmp <- NULL
for (i in 1:length(tmp$observations)){
  pheno.tmp <- c(pheno.tmp,tmp$observations[[i]]$value)

}
pheno.collect[j,] <- pheno.tmp
}
colnames(pheno.collect) <- trait.list
rownames(pheno.collect) <- file.list
pheno.collect[1:5,1:5]
pheno.collect <- data.frame(pheno.collect)

### Remove unnesecarry rows
# Get the index of elements we want to remove for now.
index_counter <- 1
index_list <- vector()
for (element in trait.list){
  if (str_sub(element,-11,-1) == "frequencies"){
   index_list <- c(index_list, index_counter)
  }
  index_counter <- index_counter + 1
}

pheno.collect <- pheno.collect[,-(index_list)]


### RANDOM NICE PLOTS
plot(pheno.collect$area.above.reference)
plot(pheno.collect$area)
print(pheno.collect)

boxplot(area ~ genotype, data= pheno.collect)
boxplot(solidity ~ genotype, data= pheno.collect)
qplot(geom = 'boxplot',genotype, area, data = pheno.collect)


     
