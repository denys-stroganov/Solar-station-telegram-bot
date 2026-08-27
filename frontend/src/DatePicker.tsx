import { useState, useRef, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface DatePickerProps {
  selectedDate: Date;
  onChange: (date: Date) => void;
  onClose: () => void;
}

const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

const WEEKDAYS = ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su'];

export default function DatePicker({ selectedDate, onChange, onClose }: DatePickerProps) {
  const [viewDate, setViewDate] = useState(new Date(selectedDate));
  const modalRef = useRef<HTMLDivElement>(null);

  // Close when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (modalRef.current && !modalRef.current.contains(event.target as Node)) {
        onClose();
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [onClose]);

  const year = viewDate.getFullYear();
  const month = viewDate.getMonth();

  const handlePrevMonth = () => {
    setViewDate(new Date(year, month - 1, 1));
  };

  const handleNextMonth = () => {
    setViewDate(new Date(year, month + 1, 1));
  };

  const getDaysInMonth = (y: number, m: number) => new Date(y, m + 1, 0).getDate();
  const getFirstDayOfMonth = (y: number, m: number) => {
    const day = new Date(y, m, 1).getDay();
    // Shift so Monday is 0 and Sunday is 6
    return day === 0 ? 6 : day - 1;
  };

  const daysInMonth = getDaysInMonth(year, month);
  const firstDay = getFirstDayOfMonth(year, month);

  const days = [];
  // Empty slots for days before the 1st of the month
  for (let i = 0; i < firstDay; i++) {
    days.push(null);
  }
  for (let i = 1; i <= daysInMonth; i++) {
    days.push(i);
  }

  const isToday = (d: number) => {
    const today = new Date();
    return today.getDate() === d && today.getMonth() === month && today.getFullYear() === year;
  };

  const isSelected = (d: number) => {
    return selectedDate.getDate() === d && selectedDate.getMonth() === month && selectedDate.getFullYear() === year;
  };

  return (
    <div className="absolute top-full mt-2 left-1/2 -translate-x-1/2 z-50">
      <div 
        ref={modalRef}
        className="bg-[#1e293b] border border-white/10 rounded-xl shadow-2xl p-4 w-72 backdrop-blur-xl"
      >
        <div className="flex justify-between items-center mb-4">
          <button 
            onClick={handlePrevMonth}
            className="p-1.5 hover:bg-white/10 rounded-lg transition-colors text-gray-400 hover:text-white"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <div className="font-semibold text-white">
            {MONTHS[month]} {year}
          </div>
          <button 
            onClick={handleNextMonth}
            className="p-1.5 hover:bg-white/10 rounded-lg transition-colors text-gray-400 hover:text-white"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>

        <div className="grid grid-cols-7 gap-1 mb-2">
          {WEEKDAYS.map(day => (
            <div key={day} className="text-center text-xs font-medium text-gray-500 py-1">
              {day}
            </div>
          ))}
        </div>

        <div className="grid grid-cols-7 gap-1">
          {days.map((day, index) => {
            if (day === null) {
              return <div key={`empty-${index}`} className="p-2" />;
            }

            const today = isToday(day);
            const selected = isSelected(day);
            
            return (
              <button
                key={day}
                onClick={() => {
                  const newDate = new Date(year, month, day);
                  if (newDate <= new Date()) { // Assuming can't select future dates based on max logic
                    onChange(newDate);
                    onClose();
                  }
                }}
                disabled={new Date(year, month, day) > new Date()}
                className={`
                  h-8 w-8 flex items-center justify-center rounded-full text-sm transition-all
                  ${selected ? 'bg-purple-600 text-white font-bold shadow-lg shadow-purple-500/30' : 
                    new Date(year, month, day) > new Date() ? 'text-gray-600 cursor-not-allowed' :
                    today ? 'text-purple-400 font-semibold border border-purple-500/30' : 
                    'text-gray-300 hover:bg-white/10'}
                `}
              >
                {day}
              </button>
            );
          })}
        </div>
        
        <div className="mt-4 pt-3 border-t border-white/10 text-center">
          <button
            onClick={() => {
              onChange(new Date());
              onClose();
            }}
            className="text-sm text-purple-400 hover:text-purple-300 font-medium transition-colors"
          >
            Today
          </button>
        </div>
      </div>
    </div>
  );
}
