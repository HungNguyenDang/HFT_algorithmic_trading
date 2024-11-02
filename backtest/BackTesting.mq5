#include <Trade\Trade.mqh>  // Include trade functions

// Variables to store file data
datetime time_open_trade;
double Entry, stop_loss, take_profit, lot;

// Arrays to store data
datetime times[];
double entries[], stop_losses[], take_profits[], Lots[];
bool executed[];

int barsTotal;

input ENUM_TIMEFRAMES Timeframe = PERIOD_M15;
input string filename = "positions.csv";

CTrade trade;

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
   
   // Open the file
   int file_handle = FileOpen(filename, FILE_READ|FILE_ANSI|FILE_COMMON);
   
   
   if(file_handle == INVALID_HANDLE)
   {
       Print("Error opening file: ", filename, ". Error: ", GetLastError());
       return(INIT_PARAMETERS_INCORRECT);
   }

   // Read data from the file
   while(!FileIsEnding(file_handle))
     {
      // Read each line
      string line = FileReadString(file_handle);
      
      // Parse the line into respective fields
      string fields[];
      StringSplit(line, ',', fields);

      // Convert and store the data
      time_open_trade = StringToTime(fields[0]);
      Entry           = NormalizeDouble(StringToDouble(fields[1]), _Digits);
      stop_loss       = NormalizeDouble(StringToDouble(fields[2]), _Digits);
      take_profit     = NormalizeDouble(StringToDouble(fields[3]), _Digits);
      lot             = NormalizeDouble(StringToDouble(fields[4]), 2);
      
      Print("Time: ", time_open_trade, ", Entry: ", Entry, ", Stop Loss: ", stop_loss, ", Take Profit: ", take_profit, ", Lot: ", lot);

      // Append to arrays
      ArrayResize(times, ArraySize(times) + 1);
      ArrayResize(entries, ArraySize(entries) + 1);
      ArrayResize(stop_losses, ArraySize(stop_losses) + 1);
      ArrayResize(take_profits, ArraySize(take_profits) + 1);
      ArrayResize(Lots, ArraySize(Lots) + 1);

      times[ArraySize(times) - 1] = time_open_trade;
      entries[ArraySize(entries) - 1] = Entry;
      stop_losses[ArraySize(stop_losses) - 1] = stop_loss;
      take_profits[ArraySize(take_profits) - 1] = take_profit;
      Lots[ArraySize(Lots) - 1] = lot;
     }

   // Close the file
   FileClose(file_handle);
   
   // Array to check executed trades
   ArrayResize(executed, ArraySize(times));
   ArrayInitialize(executed, false);

   //EventSetTimer(60);  // Set a timer event every second to check for orders
   
   barsTotal = iBars(NULL,Timeframe);
   
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   EventKillTimer();
  }

//+------------------------------------------------------------------+
//| Expert timer function                                            |
//+------------------------------------------------------------------+
void OnTick()
  {
   int bars = iBars(NULL,Timeframe);
   if(barsTotal != bars){
      barsTotal = bars;
      
      double bid = SymbolInfoDouble(_Symbol,SYMBOL_BID);
      double ask = SymbolInfoDouble(_Symbol,SYMBOL_ASK);
      
      datetime current_time = TimeCurrent();
   
      // Loop through stored positions
      for(int i = 0; i < ArraySize(times); i++)
        {
         if(times[i] == current_time)
           {
            // Ensure no previous trade is still open
            if(CheckIfNoOpenPosition())
              {
                 //double bid = SymbolInfoDouble(_Symbol,SYMBOL_BID);
                 //double ask = SymbolInfoDouble(_Symbol,SYMBOL_ASK);
                 executeSell(bid, take_profits[i], stop_losses[i], Lots[i]);
                 
                 executed[i] = true;
                 
                 Print("executed: ", entries[i], " at price: ", bid);
              }
           }
        }
      }      
  }

//+------------------------------------------------------------------+
//| Function to check if there are no open orders                    |
//+------------------------------------------------------------------+
bool CheckIfNoOpenPosition()
{
   return PositionsTotal() == 0;
}

//+------------------------------------------------------------------+
//| Function to get the close time of the last closed order          |
//+------------------------------------------------------------------+
datetime GetLastPositionCloseTime()
  {
   datetime last_close_time = 0;
   int deals = HistoryDealsTotal();
   for(int i = deals - 1; i >= 0; i--)
     {
      ulong ticket = HistoryDealGetTicket(i);
      if(ticket > 0)
        {
         datetime close_time = (datetime)HistoryDealGetInteger(ticket, DEAL_TIME);
         if(close_time > last_close_time)
           {
            last_close_time = close_time;
           }
        }
     }
   return last_close_time;
  }
  
//+------------------------------------------------------------------+

void executeBuy(double entry, double tp, double sl, double volume){

   trade.Buy(volume, NULL, entry,sl,tp);
}

void executeSell(double entry, double tp, double sl, double volume){

   trade.Sell(volume,NULL,entry,sl,tp);
}