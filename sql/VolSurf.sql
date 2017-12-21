
select o.TDaysToExp TDTE, Strike, avg(o.HedgeVol) IV, avg(ImpliedVol) IV2, avg(o.StockPrice) sPx, avg(o.pStockPrice) pPx
from 
(
select TDaysToExp, Strike, HedgeVol, ImpliedVol, StockPrice, pStockPrice
from tblOptions
where Symbol = 'SYM1'
and ESSRoot = ''
and TDaysToExp > 0
and HedgeVol > 0
and CP = 'C'
and Strike >= 0.9*StockPrice

union all

select TDaysToExp, Strike, HedgeVol, ImpliedVol, StockPrice, pStockPrice
from tblOptions
where Symbol = 'SYM1'
and ESSRoot = ''
and TDaysToExp > 0
and HedgeVol > 0
and CP = 'P'
and Strike >= 0.3*StockPrice

union all


select o.TDaysToExp, a.minX, o.HedgeVol, o.ImpliedVol, o.StockPrice, o.pStockPrice
from tblOptions o
inner join
(
select Symbol, ExpMonth, min(Strike) minX
from tblOptions
where ESSRoot = ''
and TDaysToExp > 0
and HedgeVol > 0
and Strike >= 0.3*StockPrice
group by Symbol, ExpMonth
) m
on o.Symbol = m.Symbol
and o.ExpMonth = m.ExpMonth
and o.Strike = m.minX
and o.ESSRoot = ''
and o.CP = 'P'
inner join
(
select Symbol, min(Strike) minX, max(Strike) maxX
from tblOptions
where ESSRoot = ''
and TDaysToExp > 0
and HedgeVol > 0
and Strike >= 0.3*StockPrice
group by Symbol
) a
on o.Symbol = a.Symbol
where o.Symbol = 'SYM1'


union all

select o.TDaysToExp, a.maxX, o.HedgeVol, o.ImpliedVol, o.StockPrice, o.pStockPrice
from tblOptions o
inner join
(
select Symbol, ExpMonth, max(Strike) maxX
from tblOptions
where ESSRoot = ''
and TDaysToExp > 0
and HedgeVol > 0
group by Symbol, ExpMonth
) m
on o.Symbol = m.Symbol
and o.ExpMonth = m.ExpMonth
and o.Strike = m.maxX
and o.ESSRoot = ''
and o.CP = 'C'
inner join
(
select Symbol, min(Strike) minX, max(Strike) maxX
from tblOptions
where ESSRoot = ''
and TDaysToExp > 0
and HedgeVol > 0
group by Symbol
) a
on o.Symbol = a.Symbol
where o.Symbol = 'SYM1'

) o
group by o.TDaysToExp, Strike
order by o.TDaysToExp, Strike

