library(rjson)
library(stringr)
library(ggplot2)
library(alphashape3d)
setwd("~/rens2")

#
# 3D TOP results 
# Ik laat de rest voor nu nog even weg omdat het anders wel overcrowded wordt.

# Get all files in a list
file.list <- list.files("output_subset/")
file.list <- file.list[grep("3D_top_results.txt",file.list)]

# Open one file to get dimensions
tmp <- fromJSON(file=paste0(c("output_subset/",file.list[1]),collapse = ""))
trait.list <- NULL
for (i in 1:length(tmp$observations)){
  trait.list <- c(trait.list,rep(tmp$observations[[i]]$trait,1))
}
trait.list <- c("sample_name", trait.list)

# Create dataframe for observations
pheno.collect <- data.frame(matrix(NA,nrow = 0,ncol = length(trait.list)), stringsAsFactors = FALSE)
colnames(pheno.collect) <- trait.list
# Now loop over the data and insert values into the dataframe
for ( j in 1:length(file.list)){
  tmp <- fromJSON(file=paste0(c("output_subset/",file.list[j]),collapse = ""))
  pheno.tmp <- file.list[j]
  pheno.vector <- c(file.list[j]) # Start by adding the sample name as trait. 
  if( length(tmp$observations)==33){ # check if there are enough observations, so only fully scored plants are in the dataset
  for (i in 1:length(tmp$observations)){ # Loop over values and add them to vector
    
    ## So there are traits with more than 1 value, to prevent errors we (useing paste) concatenate those values together separated by ; (so we can split later on)
    ## posiible issue later on is that values will be stored as text/string/characters, we need to as.numeric() them when we want to plot/do stats...
    
    pheno.tmp <- cbind(pheno.tmp, paste(tmp$observations[[i]]$value,collapse = ";")) # 
    #pheno.tmp <- cbind(pheno.tmp, tmp$observations[[i]]$value)
  }
  # Add new observation here
  #pheno.tmp <- data.frame(pheno.tmp, stringsAsFactors = FALSE)
  colnames(pheno.tmp) <- trait.list
  pheno.collect <- rbind(pheno.collect, pheno.tmp, stringsAsFactors = FALSE) # Now the pheno.tmp has only one row ;-)
}}

pheno.collect <- data.frame(pheno.collect, stringsAsFactors = FALSE)
dim(pheno.collect)

## simple plots
this <- ggplot(pheno.collect,aes(as.numeric(pheno.collect$solidity)))+
        geom_histogram(bins = 100)
this


this <- ggplot(pheno.collect,aes(as.numeric(pheno.collect$area),as.numeric(pheno.collect$perimeter)))+
  geom_point()+
  geom_smooth()
this

med.trait <- aggregate(as.numeric(pheno.collect$area),list(pheno.collect$genotype),median)
ril.ord <- med.trait$Group.1[order(med.trait$x)]
pheno.collect$genotype <- factor(pheno.collect$genotype,levels = ril.ord)

this <- ggplot(pheno.collect,aes(pheno.collect$genotype,as.numeric(pheno.collect$area)))+
  geom_boxplot()
this

med.trait <- aggregate(as.numeric(pheno.collect$perimeter),list(pheno.collect$genotype),median)
ril.ord <- med.trait$Group.1[order(med.trait$x)]
pheno.collect$genotype <- factor(pheno.collect$genotype,levels = ril.ord)

this <- ggplot(pheno.collect,aes(pheno.collect$genotype,as.numeric(pheno.collect$perimeter)))+
  geom_boxplot()
this

med.trait <- aggregate(as.numeric(pheno.collect$solidity),list(pheno.collect$genotype),median)
ril.ord <- med.trait$Group.1[order(med.trait$x)]
pheno.collect$genotype <- factor(pheno.collect$genotype,levels = ril.ord)

this <- ggplot(pheno.collect,aes(pheno.collect$genotype,as.numeric(pheno.collect$solidity)))+
  geom_boxplot()
this



#
# 3D Volume thingy
# currently just for one plant as test.

punten <- read.csv("~/rens2/input/0030_2018-03-14 14.21 - 238A_0_3D.csv", header=FALSE)
x <- cbind(pucolor nten[,1], punten[,2], punten[,3])
ashape3d.obj <- ashape3d(x, alpha = 1, pert = TRUE)
components_ashape3d(ashape3d.obj, 1)
plot(ashape3d.obj, byComponents = TRUE)
volume_ashape3d(ashape3d.obj, byComponents = FALSE, indexAlpha = 'all')


################## Loop for cam data #################################################################


# Get all files in a list
file.list <- list.files("output_subset/")
file.list <- file.list[grep("cam9top_results",file.list)]

tmp$observations$green_frequencies
  
# Open one file to get dimensions
tmp <- fromJSON(file=paste0(c("output_subset/",file.list[1]),collapse = ""))
trait.list <- NULL
for (i in 1:length(tmp$observations)){
  trait.list <- c(trait.list,rep(tmp$observations[[i]]$trait,1))
}
trait.list <- c("sample_name", trait.list)

# Create dataframe for observations
pheno.collect2 <- data.frame(matrix(NA,nrow = 0,ncol = length(trait.list)), stringsAsFactors = FALSE)
colnames(pheno.collect2) <- trait.list
# Now loop over the data and insert values into the dataframe
for ( j in 1:length(file.list)){
  tmp <- fromJSON(file=paste0(c("output_subset/",file.list[j]),collapse = ""))
  pheno.tmp <- file.list[j]
  pheno.vector <- c(file.list[j]) # Start by adding the sample name as trait. 
  if( length(tmp$observations)==36){ # check if there are enough observations, so only fully scored plants are in the dataset
    for (i in 1:length(tmp$observations)){ # Loop over values and add them to vector
      
      ## So there are traits with more than 1 value, to prevent errors we (useing paste) concatenate those values together separated by ; (so we can split later on)
      ## posiible issue later on is that values will be stored as text/string/characters, we need to as.numeric() them when we want to plot/do stats...
      
      pheno.tmp <- cbind(pheno.tmp, paste(tmp$observations[[i]]$value,collapse = ";")) # 
      #pheno.tmp <- cbind(pheno.tmp, tmp$observations[[i]]$value)
    }
    # Add new observation here
    #pheno.tmp <- data.frame(pheno.tmp, stringsAsFactors = FALSE)
    colnames(pheno.tmp) <- trait.list
    pheno.collect2 <- rbind(pheno.collect2, pheno.tmp, stringsAsFactors = FALSE) # Now the pheno.tmp has only one row ;-)
  }}

pheno.collect2 <- data.frame(pheno.collect2, stringsAsFactors = FALSE)
dim(pheno.collect2)


## some color data stuff, extract the counts [0-255] --> green 
tmp <- sapply(pheno.collect2$green.frequencies,strsplit,";")
names(tmp) <- pheno.collect2$sample_name
green.counts <- matrix(as.numeric(unlist(tmp)),ncol = 256)

tot.cnt <- apply(green.counts,1,sum)
val.sum <- apply(t(apply(green.counts,1,"*",0:255)),1,sum)
ave.green <- val.sum/tot.cnt

pheno.collect2 <- data.frame(pheno.collect2,ave.green)


this <- ggplot(pheno.collect2,aes(as.numeric(pheno.collect2$ave.green)))+
  geom_histogram(bins = 100)
this


this <- ggplot(pheno.collect2,aes(as.numeric(pheno.collect2$area),as.numeric(pheno.collect2$ave.green)))+
  geom_point()+
  geom_smooth()
this

med.trait <- aggregate(as.numeric(pheno.collect2$ave.green),list(pheno.collect2$genotype),median)
ril.ord <- med.trait$Group.1[order(med.trait$x)]
pheno.collect2$genotype <- factor(pheno.collect2$genotype,levels = ril.ord)

this <- ggplot(pheno.collect2,aes(pheno.collect2$genotype,as.numeric(pheno.collect2$ave.green)))+
  geom_boxplot()
this


##---> red

tmp <- sapply(pheno.collect2$red.frequencies,strsplit,";")
names(tmp) <- pheno.collect2$sample_name
red.counts <- matrix(as.numeric(unlist(tmp)),ncol = 256)

tot.cnt <- apply(red.counts,1,sum)
val.sum <- apply(t(apply(red.counts,1,"*",0:255)),1,sum)
ave.red <- val.sum/tot.cnt

pheno.collect2 <- data.frame(pheno.collect2,ave.red)


this <- ggplot(pheno.collect2,aes(as.numeric(pheno.collect2$ave.red)))+
  geom_histogram(bins = 100)
this


this <- ggplot(pheno.collect2,aes(as.numeric(pheno.collect2$ave.red)/as.numeric(pheno.collect2$ave.green)))+
  geom_histogram(bins = 100)
this



this <- ggplot(pheno.collect2,aes(as.numeric(pheno.collect2$ave.red),as.numeric(pheno.collect2$ave.green)))+
  geom_point()+
  geom_smooth()
this

med.trait <- aggregate(as.numeric(pheno.collect2$ave.red),list(pheno.collect2$genotype),median)
ril.ord <- med.trait$Group.1[order(med.trait$x)]
pheno.collect2$genotype <- factor(pheno.collect2$genotype,levels = ril.ord)

this <- ggplot(pheno.collect2,aes(pheno.collect2$genotype,as.numeric(pheno.collect2$ave.red)))+
  geom_boxplot()
this


med.trait <- aggregate(as.numeric(pheno.collect2$ave.red)/as.numeric(pheno.collect2$ave.green),list(pheno.collect2$genotype),median)
ril.ord <- med.trait$Group.1[order(med.trait$x)]
pheno.collect2$genotype <- factor(pheno.collect2$genotype,levels = ril.ord)

this <- ggplot(pheno.collect2,aes(pheno.collect2$genotype,log2(as.numeric(pheno.collect2$ave.red)/as.numeric(pheno.collect2$ave.green))))+
  geom_boxplot()
this



#### END ############################
