#' ---
#' title: "All traits"
#' ---

setwd("~/Documents/studie/master_project")
load(file="QTLdata.Rdata")
library(RcppArmadillo)
library(openxlsx)
library(ggplot2)

use.map <- rna.map[,-1]
finalframe <- pheno.collectfinal[complete.cases(pheno.collectfinalCAM),]


#' # functions
#' First we define all necessary functions
# fast qtl mapper
fast.map <- function(xm,gxpr){
  # ok <- fastLm(cbind(1,xm),as.numeric(gxpr))
  ok <- fastLm(gxpr~xm)
  pval <- pt(abs(ok$coefficients)/ok$stderr,ok$df.residual,lower.tail = F) * 2
  pval <- pval[2]
  SSyy <- sum(abs(gxpr-mean(gxpr))^2)
  SSE <- sum(abs(ok$residuals)^2) 
  R2 <- (SSyy-SSE)/SSyy
  n = length(ok$fitted.values)
  k = length(ok$coefficients)-1
  R2.adj <- 1-(SSE/SSyy)*(n-1)/(n-(k+1))
  out <- c(pval) #,R2,R2.adj)
  return(out)
}

# QTL mapper that allows cofatcors
fast.map.co <- function(xm,gxpr){
  ok <- fastLm(cbind(1,xm),as.numeric(gxpr))
  # ok <- fastLm(gxpr~xm)
  pval <- pt(abs(ok$coefficients)/ok$stderr,ok$df.residual,lower.tail = F) * 2
  pval <- pval[2]
  SSyy <- sum(abs(gxpr-mean(gxpr))^2)
  SSE <- sum(abs(ok$residuals)^2) 
  R2 <- (SSyy-SSE)/SSyy
  n = length(ok$fitted.values)
  k = length(ok$coefficients)-1
  R2.adj <- 1-(SSE/SSyy)*(n-1)/(n-(k+1))
  out <- c(pval) #,R2,R2.adj)
  return(out)
}

# needed for cofactor selection.
rem.co <- function(coset,wind){ out <- c(coset[1],coset[!coset %in% (coset[1]-wind):(coset[1]+wind)]) ; return(out) }
get.row <- function(rowno,use.map){ out <- use.map[rowno,]; return(out)}

mqm <- function(trait,use.map,wind = 100,co.p.thr = 2){
  #### start with round 1, single marker mapping 
  out <- NULL
  rnd1 <- apply(use.map,1,fast.map.co,trait)
  out$p <- rnd1
  #### further rounds, now including cofacs
  
  cofacs <- which.max(-log10(rnd1)) ## get cofact from round 1
  co.max <- -log10(rnd1)[cofacs]  ## -log10(p) value at first co-factor
  
  ### start while loop to find cofactors, only take those more signif than the threshold
  while ( co.max > co.p.thr){
    ok <- t(sapply(1:nrow(use.map),c,cofacs)) # makes list with markers to map
    co.list <- apply(ok,1,rem.co,wind) # removes cofacts when in window
    ok2 <- sapply(co.list,get.row,use.map,simplify = F) ### get all the genotypedata of the markers to map
    ok2 <- sapply(ok2,t) # flip them so the model likes them 
    pvals <- sapply(ok2,fast.map.co,trait) ## map all and collect pvalues.
    
    ##  next part is to select the next cofactor
    exclude <- c(cofacs-rep(1:wind,each=length(cofacs)),cofacs,cofacs-rep(-1*c(1:wind),each=length(cofacs))) ## make list with numbers from which the cofacts should not be selected
    exclude <- exclude[exclude > 0]
    co.pval <- -log10(pvals) ## make in to -log10
    co.pval[exclude] <- 0 ## replace the to be excluded values by 0 
    cofacs <- c(cofacs,which.max(co.pval)) ## now the next cofact is added to the list
    co.max <- -log10(pvals[which.max(co.pval)]) ### obtain the cofact significance data to do the next round of mapping
    #out$p <- rbind(out$p,pvals)  # collect data # TEMPORARILY DISABLED
    out$p <- pvals 
    
  }
  out$cofacs <- cofacs  # collect cofacs numbers
  return(out)
}

#First create an empty data frame to store all results
results <- data.frame(matrix(ncol = 4492, nrow = 0))#' # Loop with all traits
for (trait in names(finalframe[2:(length(finalframe ) - 1)])){ # Skip first and last trait because those are sample name and genotype
  print(trait)
  #mean.trait <- aggregate(finalframe[[trait]] ,list(finalframe$genotype),quantile)
  mean.trait <- aggregate(subset(finalframe[[trait]], !is.na(finalframe[[trait]])),
                          list(subset(finalframe$genotype, !is.na(finalframe[[trait]]))),quantile)
  ril.inter <- intersect(colnames(rna.map),mean.trait$Group.1)
  ril.inter <- ril.inter[!ril.inter %in% c("308A","243A")] # remove 308 and 243 as they do not have enough observations
  use.map <- rna.map[,ril.inter]
  use.trt <- mean.trait$x[,3]
  names(use.trt) <- as.character(mean.trait$Group.1)
  use.trt <- use.trt[ril.inter]
  ok <- mqm(use.trt,use.map)
  newrow <- data.frame(-log10(ok$p))
  newrow <- t(newrow)
  results <- rbind(results, newrow)
  
  chromo <- gsub("_.*","",rna.map[,1]) # Now to plot
  pos <- as.numeric(gsub(".*_","",rna.map[,1]))/1e6
  lods <- -log10(ok$p)
  to.pl <- data.frame(chromo,pos,lods)
  this <- ggplot(to.pl,aes(pos,lods)) +geom_point(size=1, na.rm = TRUE)+ 
    facet_grid(.~chromo,scale="free_x",space="free_x") +
    theme_light()+
    theme(legend.position = "top", text = element_text(size = 18), axis.text.y = element_text(size = 16), axis.text.x = element_text(size = 10))

  print(this + ggtitle(trait))
}


###################################################################### Playing with the results object

rownames(results) <- names(finalframe[2:(length(finalframe ) - 1)])
save(results, rna.map, chromo, file = "resultframe.RData")
load(file="resultframe.RData")


#Wat betreft de figuur, lijkt me een goed idee. De heatmap achtige over view heb ik met ggplot gemaakt. dmv de geom_rect functie.
#Lange lijst maken met een kolom voor trait, voor chromosome, positie, en score. Dan de xmin, ymin, xmax, en ymax voor de geom_rect berekenen en dan zou het moeten werken.
#Ik kan je er wel mee helpen of een voorbeeld schrijven als je het object met p-values hebt.

trait <- rep(rownames(results),ncol(results))
lod <- unlist(results)  # by column
xmin <- rep(seq(0.5,ncol(results)-0.5),each=nrow(results))
xmax <- rep(seq(1.5,ncol(results)+0.5),each=nrow(results))
ymin <- rep(seq(0.5,nrow(results)-0.5),ncol(results))
ymax <- rep(seq(1.5,nrow(results)+0.5),ncol(results))

to.pl <- data.frame(trait,lod,xmin,xmax,ymin,ymax)

this <- ggplot(to.pl)+
  geom_rect(aes(xmin=xmin,xmax=xmax,ymin=ymin,ymax=ymax,fill=lod))+
  scale_fill_gradientn(colors = c("grey","yellow","orange","red","magenta"))+
  scale_x_continuous(expand = c(0,0))+
  scale_y_continuous(expand =c(0,0),breaks = 1:60,labels = rownames(results))

this




### with marker chromosomes 
chr <- rep(substr(rna.map[,1],1,4),each=nrow(results))
to.pl <- data.frame(trait,lod,xmin,xmax,ymin,ymax,chr)

this <- ggplot(to.pl)+
  geom_rect(aes(xmin=xmin,xmax=xmax,ymin=ymin,ymax=ymax,fill=lod))+
  scale_fill_gradientn(colors = c("grey","yellow","orange","red","magenta"))+
  facet_grid(.~chr,scale = "free_x",space = "free_x")+
  scale_x_continuous(expand = c(0,0))+
  scale_y_continuous(expand =c(0,0),breaks = 1:60,labels = rownames(results))

this




mean.trait <- aggregate(subset(finalframe$`top sd leaf length`, !is.na(finalframe$`top sd leaf length`)),
                        list(subset(finalframe$genotype, !is.na(finalframe$`top sd leaf length`))),quantile)
ril.inter <- intersect(colnames(rna.map),mean.trait$Group.1)
ril.inter <- ril.inter[!ril.inter %in% c("308A","243A")] # remove 308 and 243 as they do not have enough observations
use.map <- rna.map[,ril.inter]
use.trt <- mean.trait$x[,3]
names(use.trt) <- as.character(mean.trait$Group.1)
use.trt <- use.trt[ril.inter]
ok <- mqm(use.trt,use.map)


chromo <- gsub("_.*","",rna.map[,1]) # Now to plot
pos <- as.numeric(gsub(".*_","",rna.map[,1]))/1e6
lods <- -log10(ok$p)
to.pl <- data.frame(chromo,pos,lods)
this <- ggplot(to.pl,aes(pos,lods)) +geom_point(size=1, na.rm = TRUE)+ 
  facet_grid(.~chromo,scale="free_x",space="free_x") +
  theme_light()+
  theme(legend.position = "top", text = element_text(size = 18), axis.text.y = element_text(size = 16), axis.text.x = element_text(size = 10))


this
