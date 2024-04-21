# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

def lanchester_model(y, t, alpha, beta, kt, ki):
    Nt, Ni = y
    Ft = kt * Nt
    Fi = ki * Ni
    dNtdt = -alpha * Fi
    dNidt = -beta * Ft
    return [dNtdt, dNidt]

def runge_kutta(y, t, h, alpha, beta, kt, ki):
    k1 = h * np.array(lanchester_model(y, t, alpha, beta, kt, ki))
    k2 = h * np.array(lanchester_model(y + 0.5 * k1, t + 0.5 * h, alpha, beta, kt, ki))
    k3 = h * np.array(lanchester_model(y + 0.5 * k2, t + 0.5 * h, alpha, beta, kt, ki))
    k4 = h * np.array(lanchester_model(y + k3, t + h, alpha, beta, kt, ki))
    return y + (k1 + 2 * k2 + 2 * k3 + k4) / 6


def show_description():
    description_text = """
    F_t = k_t * N_t
    F_i = k_i * N_i

    dN_t/dt = -alpha * F_i
    dN_i/dt = -beta * F_t

    где:
    F_t и F_i - силы танков и пехоты соответственно,
    N_t и N_i - численность танков и пехоты,
    k_t и k_i - коэффициенты пропорциональности.

    Уравнение для изменения численности может быть записано как:

    dN_t/dt = -alpha * F_i
    dN_i/dt = -beta * F_t

    где alpha и beta - коэффициенты, отражающие влияние военных действий на изменение численности.

    Эта модель предполагает, что танки и пехота взаимодействуют между собой, и результат боя зависит от их относительной эффективности и численности. Коэффициенты k_t и k_i могут быть настроены в зависимости от реальных характеристик техники и пехоты, например, с учетом военной доктрины, обучения и тактики.
    """
    description_window = tk.Toplevel(window)
    description_window.title("Описание задачи")

    description_label = ttk.Label(description_window, text=description_text, wraplength=600, justify="left")
    description_label.pack(padx=10, pady=10)

def set_test_conditions():
    # Установка тестовых значений
    alpha_entry.delete(0, tk.END)
    alpha_entry.insert(0, "0.01")
    beta_entry.delete(0, tk.END)
    beta_entry.insert(0, "0.01")
    kt_entry.delete(0, tk.END)
    kt_entry.insert(0, "1")
    ki_entry.delete(0, tk.END)
    ki_entry.insert(0, "1")
    Nt0_entry.delete(0, tk.END)
    Nt0_entry.insert(0, "100")
    Ni0_entry.delete(0, tk.END)
    Ni0_entry.insert(0, "100")
    steps_entry.delete(0, tk.END)
    steps_entry.insert(0, "1000")

    # Автоматический запуск построения графика
    plot_graph()
def plot_graph():
    alpha = float(alpha_entry.get())
    beta = float(beta_entry.get())
    kt = float(kt_entry.get())
    ki = float(ki_entry.get())

    Nt0 = float(Nt0_entry.get())
    Ni0 = float(Ni0_entry.get())
    y0 = [Nt0, Ni0]

    t0 = 0
    t_end = 800
    num_steps = int(steps_entry.get())
    h = (t_end - t0) / num_steps

    # Измененный временной интервал в часах
    t_hours = np.linspace(t0, t_end * 60, num_steps + 1)

    solution = np.zeros((num_steps + 1, 2))
    solution[0, :] = y0

    text_output.delete('1.0', tk.END)  # Очистка текстового поля перед новым выводом
    treeview.delete(*treeview.get_children())  # Очистка таблицы перед новым выводом

    plot_cutoff = cutoff_checkbox.get()  # Получаем состояние чекбокса

    for i in range(num_steps):
        y0 = runge_kutta(y0, t_hours[i], h, alpha, beta, kt, ki )
        solution[i + 1, :] = y0

        # Если включена отсечка и одна из сторон уменьшилась до 30%, то прерываем построение графика
        if plot_cutoff and (solution[i + 1, 0] <= 0.3 * Nt0 or solution[i + 1, 1] <= 0.3 * Ni0):
            break

        # Вывод информации о шагах в текстовое поле
        text_output.insert(tk.END, f"Шаг {i + 1}:\n")
        text_output.insert(tk.END, f"    Время: {t_hours[i + 1] / 60:.2f} \n")
        text_output.insert(tk.END, f"    Танки: {solution[i + 1, 0]:.2f}\n")
        text_output.insert(tk.END, f"    Пехота: {solution[i + 1, 1]:.2f}\n")
        text_output.insert(tk.END, "\n")

        # Добавление данных в таблицу
        treeview.insert("", "end", values=(t_hours[i + 1] / 60, solution[i + 1, 0], solution[i + 1, 1]))

    ax1.clear()
    ax1.plot(t_hours / 60, solution[:, 0], label='Танки', color='blue')  # Обновлено: деление на 60
    ax1.set_ylabel('Численность танков')
    ax1.set_ylim(bottom=0)  # Устанавливаем нижний предел оси y в 0
    ax1.legend()

    ax2.clear()
    ax2.plot(t_hours / 60, solution[:, 1], label='Пехота', color='orange')  # Обновлено: деление на 60
    ax2.set_xlabel('Время (минуты)')
    ax2.set_ylabel('Численность пехоты')
    ax2.set_ylim(bottom=0)  # Устанавливаем нижний предел оси y в 0
    ax2.legend()

    canvas.draw()

# Создание графического интерфейса
window = tk.Tk()
window.title("Модель Ланчестера")

# Стиль ttk для улучшения внешнего вида
style = ttk.Style()
style.configure("TLabel", padding=5)
style.configure("TButton", padding=(5, 5, 5, 5), font='Helvetica 10')

# Ввод параметров
parameters_frame = ttk.LabelFrame(window, text="Параметры модели")
parameters_frame.grid(row=0, column=0, padx=10, pady=10, sticky='w')

ttk.Label(parameters_frame, text="alpha:").grid(row=0, column=0, sticky='e')
alpha_entry = ttk.Entry(parameters_frame)
alpha_entry.grid(row=0, column=1)

ttk.Label(parameters_frame, text="beta:").grid(row=1, column=0, sticky='e')
beta_entry = ttk.Entry(parameters_frame)
beta_entry.grid(row=1, column=1)

ttk.Label(parameters_frame, text="kt:").grid(row=2, column=0, sticky='e')
kt_entry = ttk.Entry(parameters_frame)
kt_entry.grid(row=2, column=1)

ttk.Label(parameters_frame, text="ki:").grid(row=3, column=0, sticky='e')
ki_entry = ttk.Entry(parameters_frame)
ki_entry.grid(row=3, column=1)


# Начальные условия
initial_conditions_frame = ttk.LabelFrame(window, text="Начальные условия")
initial_conditions_frame.grid(row=1, column=0, padx=10, pady=10, sticky='w')

ttk.Label(initial_conditions_frame, text="Nt0:").grid(row=0, column=0, sticky='e')
Nt0_entry = ttk.Entry(initial_conditions_frame)
Nt0_entry.grid(row=0, column=1)

ttk.Label(initial_conditions_frame, text="Ni0:").grid(row=1, column=0, sticky='e')
Ni0_entry = ttk.Entry(initial_conditions_frame)
Ni0_entry.grid(row=1, column=1)

# Добавление чекбокса для отсечки графика
cutoff_checkbox = tk.IntVar()
cutoff_checkbox.set(0)  # Изначально отсечка выключена
cutoff_checkbox_label = ttk.Checkbutton(window, text="Отсечка графика при 30%", variable=cutoff_checkbox)
cutoff_checkbox_label.grid(row=6, column=2, columnspan=2, pady=5)

# Количество шагов и начальный шаг
steps_frame = ttk.LabelFrame(window, text="Параметры интеграции")
steps_frame.grid(row=2, column=0, padx=10, pady=10, sticky='w')

ttk.Label(steps_frame, text="Количество шагов:").grid(row=0, column=0, sticky='e')
steps_entry = ttk.Entry(steps_frame)
steps_entry.grid(row=0, column=1)

# Кнопка для тестирования
test_button = ttk.Button(window, text="Тестирование", command=set_test_conditions)
test_button.grid(row=7, column=0, columnspan=3, pady=10)

# Графики
fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(6, 4))
canvas = FigureCanvasTkAgg(fig, master=window)
canvas_widget = canvas.get_tk_widget()
canvas_widget.grid(row=0, column=1, rowspan=3, padx=10, pady=10)

# Текстовое поле для вывода информации о шагах
text_output = ScrolledText(window, width=40, height=10)
text_output.grid(row=3, column=0, columnspan=2, pady=10)

# Таблица для вывода данных
columns = ("Время", "Танки", "Пехота")
treeview = ttk.Treeview(window, columns=columns, show="headings")
treeview.heading("Время", text="Время")
treeview.heading("Танки", text="Танки")
treeview.heading("Пехота", text="Пехота")
treeview.grid(row=0, column=2, rowspan=3, padx=10, pady=10)

# Кнопка для построения графиков
plot_button = ttk.Button(window, text="Построить графики", command=plot_graph)
plot_button.grid(row=4, column=0, columnspan=3, pady=10)

# Кнопка для отображения описания
description_button = ttk.Button(window, text="Описание задачи", command=show_description)
description_button.grid(row=6, column=0, columnspan=2, pady=10)

window.mainloop()
