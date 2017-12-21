

select TradeDate, AdjClose Px, SMA50, SMA200, 
ImpliedVol1M IV1M, ImpliedVol63 IV3M, ImpliedVol252 IVFar, TheoVol63 TV,
IVSkew63 Skew3M, IVSkew252 SkewFar, TVSkew,
EventType
from tblStockHistory
where TradeDate >= 'DATE1'
and Symbol = 'SYM1'
order by TradeDate

