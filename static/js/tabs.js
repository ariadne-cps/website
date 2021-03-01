(function(){'use strict'
let tabsClass='tabs'
let tabClass='tab'
let tabButtonClass='tab-button'
let activeClass='active'
function activateTab(chosenTabElement){let tabList=chosenTabElement.parentNode.querySelectorAll('.'+tabClass)
for(let i=0;i<tabList.length;i++){let tabElement=tabList[i]
if(tabElement.isEqualNode(chosenTabElement)){tabElement.classList.add(activeClass)}else{tabElement.classList.remove(activeClass)}}}
let tabbedContainers=document.body.querySelectorAll('.'+tabsClass)
for(let i=0;i<tabbedContainers.length;i++){let tabbedContainer=tabbedContainers[i]
let tabList=tabbedContainer.querySelectorAll('.'+tabClass)
activateTab(tabList[0])
for(let i=0;i<tabList.length;i++){let tabElement=tabList[i]
let tabButton=tabElement.querySelector('.'+tabButtonClass)
tabButton.addEventListener('click',function(event){event.preventDefault()
activateTab(event.target.parentNode)})}}})()