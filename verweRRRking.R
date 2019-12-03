library(rjson)
library(stringr)
library(ggplot2)
library(alphashape3d)

############################################################# TOP PERSPECTIVE RGB IMAGE
## Load data
setwd("~/studie/master/data/")

## get data
file.list <- list.files("output/")
file.list <- file.list[grep("cam9top_results.txt",file.list)]

## open one temp file
tmp <- fromJSON(file=paste0(c("output/",file.list[1]),collapse = ""))

trait.list <- NULL
for (i in 1:length(tmp$observations)){
  trait.list <- c(trait.list,rep(tmp$observations[[i]]$trait,length(tmp$observations[[i]]$value)))
}
tmp$observations$genotype$value


pheno.collect <- matrix(NA,nrow = length(file.list),ncol = length(trait.list))
for ( j in 1:length(file.list)){
tmp <- fromJSON(file=paste0(c("output/",file.list[j]),collapse = ""))
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

boxplot(area ~ genotype, data= pheno.collect)
boxplot(solidity ~ genotype, data= pheno.collect)
qplot(geom = 'boxplot',genotype, area, data = pheno.collect)



##################################################################################### TOP perspective 3D data
## Load data
setwd("~/studie/master/data/")

## get data
file.list <- list.files("output/")
file.list <- file.list[grep("3D_top_results.txt",file.list)]

## open one temp file
tmp <- fromJSON(file=paste0(c("output/",file.list[1]),collapse = ""))

trait.list <- NULL
for (i in 1:length(tmp$observations)){
  trait.list <- c(trait.list,rep(tmp$observations[[i]]$trait,length(tmp$observations[[i]]$value)))
}
tmp$observations$genotype$value


pheno.collect <- matrix(NA,nrow = length(file.list),ncol = length(trait.list))
for ( j in 1:length(file.list)){
  tmp <- fromJSON(file=paste0(c("output/",file.list[j]),collapse = ""))
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

boxplot(pheno.collect$convex.hull.area ~  pheno.collect$genotype)
boxplot(pheno.collect$perimeter ~  pheno.collect$genotype)
boxplot(pheno.collect$longest.path ~  pheno.collect$genotype)
boxplot(pheno.collect$width ~  pheno.collect$genotype)

boxplot(area ~ genotype, data= pheno.collect)
boxplot(solidity ~ genotype, data= pheno.collect)
qplot(geom = 'boxplot',genotype, area, data = pheno.collect)

############################################################# SIDE PERSPECTIVE RGB IMAGE
## Load data
setwd("~/studie/master/data/")

## get data
file.list <- list.files("output/")
file.list <- file.list[grep("cam0side_results.txt",file.list)]


## open one temp file
tmp <- fromJSON(file=paste0(c("output/",file.list[1]),collapse = ""))

trait.list <- NULL
for (i in 1:length(tmp$observations)){
  trait.list <- c(trait.list,rep(tmp$observations[[i]]$trait,length(tmp$observations[[i]]$value)))
}
tmp$observations$genotype$value

pheno.collect <- matrix(NA,nrow = length(file.list),ncol = length(trait.list))
for ( j in 1:length(file.list)){
  tmp <- fromJSON(file=paste0(c("output/",file.list[j]),collapse = ""))
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

boxplot(area ~ genotype, data= pheno.collect)
boxplot(solidity ~ genotype, data= pheno.collect)
boxplot(pheno.collect$longest.path ~ pheno.collect$genotype)
boxplot(pheno.collect$height ~ pheno.collect$genotype)
qplot(geom = 'boxplot',genotype, area, data = pheno.collect)

############################################################# SIDE PERSPECTIVE 3D data
## Load data
setwd("~/studie/master/data/")

## get data
file.list <- list.files("output/")
file.list <- file.list[grep("3D_side_results.txt",file.list)]

## open one temp file
tmp <- fromJSON(file=paste0(c("output/",file.list[1]),collapse = ""))

trait.list <- NULL
for (i in 1:length(tmp$observations)){
  trait.list <- c(trait.list,rep(tmp$observations[[i]]$trait,length(tmp$observations[[i]]$value)))
}
tmp$observations$genotype$value

pheno.collect <- matrix(NA,nrow = length(file.list),ncol = length(trait.list))
for ( j in 1:length(file.list)){
  tmp <- fromJSON(file=paste0(c("output/",file.list[j]),collapse = ""))
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

boxplot(area ~ genotype, data= pheno.collect)
boxplot(solidity ~ genotype, data= pheno.collect)
boxplot(pheno.collect$longest.path ~ pheno.collect$genotype)
boxplot(pheno.collect$height ~ pheno.collect$genotype)
  qplot(geom = 'boxplot',genotype, area, data = pheno.collect)


############### Volume thingy
#punten <- read.csv("C:/Users/RensD/Documents/studie/master/Offline_version/top_input/0004_2018-02-21 13.44 - 21_0_3D.csv")
punten <- read.csv("~/Big_project/input/0003_2018-02-21 13.44 - 21_0_3D.csv", header=FALSE)


View(punten)
x <- cbind(punten[,1], punten[,2], punten[,3])
ashape3d.obj <- ashape3d(x, alpha = 0.75, pert = TRUE)
components_ashape3d(ashape3d.obj, 1)
plot(ashape3d.obj, byComponents = TRUE)
volume_ashape3d(ashape3d.obj, byComponents = TRUE)
    
