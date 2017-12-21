
select TDaysToExp TDTE, Strike, avg(ImpliedVol) IV, avg(PrevIVol) pIV, avg(StockPrice) sPx, avg(pStockPrice) pPx
from
(
select *
from tblOptions
where Symbol = 'SYM1'
and ESSRoot = ''
and TDaysToExp > 4
and ImpliedVol > 0
and Strike < 1.0*StockPrice
and Strike > 0.7*StockPrice
and CP = 'P'
and abs(HedgeDelta) >= 0.1

union all

select *
from tblOptions
where Symbol = 'SYM1'
and ESSRoot = ''
and TDaysToExp > 4
and ImpliedVol > 0
and Strike > 0.95*StockPrice
and Strike < 1.3*StockPrice
and CP = 'C'
and abs(HedgeDelta) >= 0.1

) a
group by TDaysToExp, Strike
order by TDaysToExp, Strike

