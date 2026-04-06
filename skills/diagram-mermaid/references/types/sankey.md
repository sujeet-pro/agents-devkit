# Sankey Diagram

**Directive:** `sankey-beta`

**Syntax (CSV-like):**

```
sankey-beta

Source,Target,Value
Source1,Target1,25
Source1,Target2,15
Source2,Target1,10
```

**Example:**

```
%% Diagram: Request Traffic Flow
%% Type: sankey
sankey-beta

CDN,API Gateway,500
CDN,Static Assets,300
API Gateway,Auth Service,200
API Gateway,User Service,150
API Gateway,Order Service,150
Auth Service,Cache,120
Auth Service,Database,80
User Service,Database,100
User Service,Cache,50
Order Service,Database,130
Order Service,Message Queue,20
```
