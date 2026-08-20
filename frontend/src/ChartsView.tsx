import { useState, useEffect } from 'react';
import { BarChart2, Calendar, RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react';
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';

interface ChartDataItem {
  time: string;
  year: number;
  month: number;
  day: number;
  hour: number;
  minute: number;
  second: number;
  solarPv: number;
  gridPower: number;
  batteryDischarging: number;
  consumption: number;
  soc: number;
  acCouplePower: number;
}

const UA_MONTHS = [
  'Січ', 'Лют', 'Бер', 'Кві', 'Тра', 'Чер',
  'Лип', 'Сер', 'Вер', 'Жов', 'Лис', 'Гру'
];

export default function ChartsView() {
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [data, setData] = useState<ChartDataItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const getApiUrl = (path: string) => {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      return `http://localhost:8080${path}`;
    }
    return path;
  };

  const formatDateParam = (date: Date) => {
    const yyyy = date.getFullYear();
    const mm = String(date.getMonth() + 1).padStart(2, '0');
    const dd = String(date.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
  };

  const fetchData = async (date: Date) => {
    setLoading(true);
    setError(null);
    try {
      const dateStr = formatDateParam(date);
      const res = await fetch(getApiUrl(`/api/stats/chart?date=${dateStr}`)).then(r => r.json());

      if (res.success) {
        setData(res.data || []);
      } else {
        throw new Error(res.error || 'Failed to fetch chart data');
      }
    } catch (err: any) {
      setError(err.message || 'Помилка підключення до сервера');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData(selectedDate);
  }, [selectedDate]);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchData(selectedDate);
  };

  const handlePrev = () => {
    const newDate = new Date(selectedDate);
    newDate.setDate(newDate.getDate() - 1);
    setSelectedDate(newDate);
  };

  const handleNext = () => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const selected = new Date(selectedDate);
    selected.setHours(0, 0, 0, 0);

    if (selected >= today) return;

    const newDate = new Date(selectedDate);
    newDate.setDate(newDate.getDate() + 1);
    setSelectedDate(newDate);
  };

  const isToday = () => {
    const today = new Date();
    return (
      selectedDate.getDate() === today.getDate() &&
      selectedDate.getMonth() === today.getMonth() &&
      selectedDate.getFullYear() === today.getFullYear()
    );
  };

  // ticks for every 4 hours: 00:00, 04:00, 08:00, 12:00, 16:00, 20:00
  // we'll format the time string (e.g. "2026-08-20 04:15:00") into just "04:15" 
  const formatXAxis = (tickItem: string) => {
    const parts = tickItem.split(' ');
    if (parts.length > 1) {
      const timeParts = parts[1].split(':');
      return `${timeParts[0]}:${timeParts[1]}`;
    }
    return tickItem;
  };

  // Prepare data with parsed hours for better X axis layout
  const chartData = data.map(item => ({
    ...item,
    timeFormatted: formatXAxis(item.time),
    solarPvKw: item.solarPv / 1000,
    gridPowerKw: item.gridPower / 1000,
    batteryKw: item.batteryDischarging / 1000,
    consumptionKw: item.consumption / 1000,
  }));

  const tickValues = chartData
    .filter(item => item.minute === 0 && item.hour % 4 === 0)
    .map(item => item.timeFormatted);

  if (tickValues.length === 0 && chartData.length > 0) {
    // fallback if exactly :00 is not found
    const first = chartData[0];
    tickValues.push(first.timeFormatted);
  }

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#1e293b]/90 border border-white/10 rounded-lg p-3 text-sm shadow-xl backdrop-blur-sm">
          <p className="text-gray-300 font-semibold mb-2">{label}</p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center gap-2 mb-1">
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
              <span className="text-gray-400">{entry.name}:</span>
              <span className="text-white font-medium">
                {entry.value.toFixed(1)} {entry.dataKey === 'soc' ? '%' : 'kW'}
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  if (loading && !refreshing) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-[#090b11] text-gray-400">
        <RefreshCw className="w-10 h-10 animate-spin text-purple-500 mb-4" />
        <p className="text-sm font-medium animate-pulse">Завантаження графіків...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-[#090b11] text-gray-400 p-6 text-center">
        <div className="bg-red-500/10 border border-red-500/20 rounded-2xl p-6 max-w-md">
          <p className="text-red-400 font-medium mb-4">⚠️ Помилка: {error}</p>
          <button
            onClick={() => fetchData(selectedDate)}
            className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-xl transition-all"
          >
            Спробувати знову
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#090b11] text-gray-100 p-4 pb-12 max-w-lg mx-auto font-sans">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
            <BarChart2 className="text-purple-500 w-6 h-6" />
            Графіки
          </h1>
          <p className="text-xs text-gray-500">Luxpower WManage API</p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="p-2.5 rounded-xl glass-panel-light text-gray-400 hover:text-white transition-all active:scale-95"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin text-purple-500' : ''}`} />
        </button>
      </div>

      {/* Date Navigation Bar */}
      <div className="flex items-center justify-between bg-[#121824] p-3 rounded-xl mb-6 border border-white/5">
        <button
          onClick={handlePrev}
          className="p-2 hover:bg-[#1e293b] rounded-lg transition-all text-gray-400 hover:text-white"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>
        <div className="flex items-center gap-2 font-medium">
          <Calendar className="w-4 h-4 text-purple-500" />
          <span className="text-white text-lg">
            {selectedDate.getDate()} {UA_MONTHS[selectedDate.getMonth()]} {selectedDate.getFullYear()}
          </span>
        </div>
        <button
          onClick={handleNext}
          disabled={isToday()}
          className={`p-2 rounded-lg transition-all ${isToday() ? 'opacity-30 cursor-not-allowed text-gray-600' : 'hover:bg-[#1e293b] text-gray-400 hover:text-white'
            }`}
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </div>

      {/* Charts */}
      {chartData.length === 0 ? (
        <div className="text-center text-gray-500 py-10 bg-[#121824] rounded-2xl border border-white/5">
          Немає даних за цей день
        </div>
      ) : (
        <div className="space-y-6">

          {/* Solar PV Chart */}
          <div className="bg-[#121824] p-4 rounded-2xl border border-white/5">
            <h3 className="text-yellow-400 font-semibold mb-4 text-sm">Генерація (kW)</h3>
            <div className="h-48 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorSolar" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#eab308" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#eab308" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                  <XAxis dataKey="timeFormatted" stroke="#ffffff50" fontSize={12} tickMargin={10} minTickGap={30} ticks={tickValues} />
                  <YAxis stroke="#ffffff50" fontSize={12} tickFormatter={(val) => val.toFixed(1)} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="solarPvKw" name="Solar PV" stroke="#eab308" strokeWidth={2} fillOpacity={1} fill="url(#colorSolar)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Consumption Chart */}
          <div className="bg-[#121824] p-4 rounded-2xl border border-white/5">
            <h3 className="text-rose-400 font-semibold mb-4 text-sm">Споживання (kW)</h3>
            <div className="h-48 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorCons" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#fb7185" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#fb7185" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                  <XAxis dataKey="timeFormatted" stroke="#ffffff50" fontSize={12} tickMargin={10} minTickGap={30} ticks={tickValues} />
                  <YAxis stroke="#ffffff50" fontSize={12} tickFormatter={(val) => val.toFixed(1)} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="consumptionKw" name="Consumption" stroke="#fb7185" strokeWidth={2} fillOpacity={1} fill="url(#colorCons)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Battery Chart */}
          <div className="bg-[#121824] p-4 rounded-2xl border border-white/5">
            <h3 className="text-emerald-400 font-semibold mb-4 text-sm">Розряд акумулятора (kW)</h3>
            <div className="h-48 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorBat" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#34d399" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#34d399" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                  <XAxis dataKey="timeFormatted" stroke="#ffffff50" fontSize={12} tickMargin={10} minTickGap={30} ticks={tickValues} />
                  <YAxis stroke="#ffffff50" fontSize={12} tickFormatter={(val) => val.toFixed(1)} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="batteryKw" name="Battery" stroke="#34d399" strokeWidth={2} fillOpacity={1} fill="url(#colorBat)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Grid Chart */}
          <div className="bg-[#121824] p-4 rounded-2xl border border-white/5">
            <h3 className="text-sky-400 font-semibold mb-4 text-sm">Енергія з/в мережу (kW)</h3>
            <div className="h-48 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorGrid" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#38bdf8" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                  <XAxis dataKey="timeFormatted" stroke="#ffffff50" fontSize={12} tickMargin={10} minTickGap={30} ticks={tickValues} />
                  <YAxis stroke="#ffffff50" fontSize={12} tickFormatter={(val) => val.toFixed(1)} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="gridPowerKw" name="Grid Power" stroke="#38bdf8" strokeWidth={2} fillOpacity={1} fill="url(#colorGrid)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* SOC Chart */}
          <div className="bg-[#121824] p-4 rounded-2xl border border-white/5">
            <h3 className="text-purple-400 font-semibold mb-4 text-sm">Заряд Акумуляторів (%)</h3>
            <div className="h-48 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 5, right: 0, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorSoc" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#c084fc" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#c084fc" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                  <XAxis dataKey="timeFormatted" stroke="#ffffff50" fontSize={12} tickMargin={10} minTickGap={30} ticks={tickValues} />
                  <YAxis stroke="#ffffff50" fontSize={12} domain={[0, 100]} />
                  <Tooltip content={<CustomTooltip />} />
                  <Area type="monotone" dataKey="soc" name="SOC" stroke="#c084fc" strokeWidth={2} fillOpacity={1} fill="url(#colorSoc)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

        </div>
      )}
    </div>
  );
}
