import os
import sys
import tkinter.messagebox
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import TextBox, Button, RadioButtons
from matplotlib.animation import FuncAnimation

os.system("cls")


class Info:
    sample_rate = 200
    sample_interval = 1 / sample_rate
    time = np.arange(0, 3, sample_interval)
    graph_adjust = 5


class UltraPlot(object):
    def __init__(self, plot, figure, title) -> None:
        self.subplot = plot
        self.figure = figure
        self.y_text = self.subplot.text(3.2, 5, "")
        self.subplot.title.set_text(title)
        self.subplot.set_xlabel("t(s)")
        self.subplot.set_ylabel("y(m)")
        # self.subplot.set_ylabel("y(1, t)")
        # self.subplot.grid()


class SubPlot(UltraPlot):
    def __init__(self, plot, figure, title, amplitude, lambda_, omega) -> None:
        super().__init__(plot=plot, figure=figure, title=title)
        self.type = "senoidal"
        self.amplitude = amplitude
        self.lambda_ = lambda_
        self.omega = omega
        self.k = (2 * np.pi) / self.lambda_
        self.y_calc = self.get_calc(0)
        (self.line,) = self.subplot.plot(Info().time, self.y_calc)
        self.subplot.set_ylim(
            [
                -self.amplitude - Info().graph_adjust,
                self.amplitude + Info().graph_adjust,
            ]
        )

    # * Atualiza os valores do calculo para o calculo da onda
    def update_values(self, amplitude, omega, lambda_):         
        self.amplitude = amplitude
        self.lambda_ = lambda_
        self.omega = omega
        self.subplot.set_ylim(
            [
                -abs(self.amplitude) - Info().graph_adjust,
                abs(self.amplitude) + Info().graph_adjust,
            ]
        )

    # * retorna os valores do calculo da onda
    def get_calc(self, velocity):
        y = (self.k + self.omega * Info().time) + velocity

        # * Onda senoidal
        if self.type == "senoidal":
            y_calc = self.amplitude * np.sin(y)

        # * Onda quadrada
        elif self.type == "quadrada":
            y_calc = self.amplitude * np.sign(np.sin(y))

        # * Onda triangular
        elif self.type == "triangular":
            y_calc = self.amplitude * np.arcsin(np.sin(y))

        # * Onda serrada
        elif self.type == "serrada":
            y_calc = -self.amplitude * np.arctan(np.cos(y) / np.sin(y))

        return y_calc


class ResultPlot(UltraPlot):
    def __init__(self, plot, plot_1, plot_2, figure, title) -> None:
        super().__init__(plot=plot, figure=figure, title=title)
        self.plot_1 = plot_1
        self.plot_2 = plot_2
        self.y_calc = self.plot_1.line.get_ydata() + self.plot_2.line.get_ydata()
        (self.line,) = self.subplot.plot(Info().time, self.y_calc)
        self.lambda_ = 0
        self.amplitude = abs(self.plot_1.amplitude) + abs(self.plot_2.amplitude)
        self.subplot.set_ylim(
            [
                -self.amplitude - Info().graph_adjust,
                self.amplitude + Info().graph_adjust,
            ]
        )

    # * Atualiza os valores do calculo da onda somando os valores da 1ª onda com os valores da 2º onda
    def update_values(self):
        self.amplitude = abs(self.plot_1.amplitude) + abs(self.plot_2.amplitude)
        self.subplot.set_ylim(
            [
                -self.amplitude - Info().graph_adjust,
                self.amplitude + Info().graph_adjust,
            ]
        )

    # * Retorna os valores do calculo da onda
    def get_calc(self, velocity):
        self.y_calc = self.plot_1.line.get_ydata() + self.plot_2.line.get_ydata()
        return self.y_calc


class Input:
    def __init__(
        self,
        amplitude_text,
        omega_text,
        lambda_text,
        button,
        radio_buttons,
        plot,
        resultPlot,
    ):
        # * Caixa de texto para a inserção da amplitude
        self.amplitude_text = amplitude_text
        # * Caixa de texto para a inserção do omega        
        self.omega_text = omega_text
        # * Caixa de texto para a inserção do lambda                      
        self.lambda_text = lambda_text
        # * Botão que captura as informações e atualiza o cálculo das ondas                    
        self.button = button                              
        # * Gráfico
        self.plot = plot
        # * Gráfico resultante (3º gráfico)                                  
        self.resultPlot = resultPlot
         # * Botões para a escolha do tipo de onda                      
        self.radio_buttons = radio_buttons
        # * Relaciona o botão de atualizar a base de cálculo da onda com a função de atualizar a base da cálculo da onda               
        self.button.on_clicked(self.button_action)
         # * Relaciona o botão de escolher o tipo de onda com a função de alterar o tipo de onda        
        self.radio_buttons.on_clicked(self.radio_action) 

    # * Quando o botão é apertado atualiza os valores do calculo da onda
    def button_action(self, event):
        # * Verifica se lambda é menor que 0                     
        if float(self.lambda_text.text) < 0:
            tkinter.messagebox.showerror("Erro!", "Cumprimento de onda não pode ser menor que 0!")
            self.lambda_text.set_val(self.plot.lambda_)
        # * Verifica se omega é menor que 0 
        elif float(self.omega_text.text) < 0:
            tkinter.messagebox.showerror("Erro!", "Frequência angular não pode ser menor que 0!")
            self.omega_text.set_val(self.plot.omega)
            
        else:
            self.plot.update_values(
                float(self.amplitude_text.text),
                float(self.omega_text.text),
                float(self.lambda_text.text),
            )

            self.resultPlot.update_values()

    # * Altera o tipo de onda baseado na escolha do usuário
    def radio_action(self, event):                        
        self.plot.type = event


class Graph:
    def __init__(self) -> None:
        # * Estrutura com os 3 gráficos
        self.figure, self.ax = plt.subplots(3, 1)
        self.figure.canvas.set_window_title("Superposição de Ondas")
        self.figure.set_facecolor("#dee2e6")

        # ? Os 2 primeiros gráficos
        # * Subplot(plot, figure, titulo, amplitude, lambda_, omega)
        self.plot_1 = SubPlot(self.ax[0], self.figure, "Onda 1", 0, 1, 0)
        self.plot_2 = SubPlot(self.ax[1], self.figure, "Onda 2", 0, 1, 0)

        # ? Gráfico resultante da soma dos 2 anteriores
        # * Resultplot(plot, gráfico 1, gráfico 2, figure, título)
        self.result_plot = ResultPlot(
            self.ax[2], self.plot_1, self.plot_2, self.figure, "Resultado"
        )

        # * Lista com o 3 gráficos
        self.plots = [self.plot_1, self.plot_2, self.result_plot]

        # * Lista com as 3 linhas (ondas que aparecem em cada gráfico)
        self.lines = [plot.line for plot in self.plots]

        # * Lista com o 3 textos do lado direito das ondas
        self.y_texts = [plot.y_text for plot in self.plots]

        # * Ajuste de posição dos gráficos
        plt.subplots_adjust(bottom=0.145, top=0.96, hspace=0.5)

        # * Configuração dos botões, caixas de texto, radio buttons e a tecla enter
        self.setup_inputs()

        # * Loop da animação
        self.animation = FuncAnimation(
            self.figure, self.animate, np.arange(1, 300), interval=25, blit=True
        )

        # * Pausar animação
        self.paused = False

        # * Visualizar gráfico na tela
        plt.show()

    # * Configuração dos botões, caixas de texto, radio buttons e a tecla enter
    def setup_inputs(self):
        x = 0.1
        y = 0.01

        self.plot_1_input = Input(
            TextBox(plt.axes([x, y, 0.06, 0.05]), "A1", initial=""),
            TextBox(plt.axes([x + 0.10, y, 0.06, 0.05]), "ω1", initial=""),
            TextBox(plt.axes([x + 0.20, y, 0.06, 0.05]), "λ1", initial=""),
            Button(plt.axes([x + 0.28, y, 0.12, 0.05]), "Onda 1 ⥁"),
            RadioButtons(
                plt.axes([0.005, 0.8, 0.08, 0.1]),
                ("senoidal", "quadrada", "triangular", "serrada"),
            ),
            self.plot_1,
            self.result_plot,
        )

        self.plot_2_input = Input(
            TextBox(plt.axes([x + 0.45, y, 0.06, 0.05]), "A2", initial=""),
            TextBox(plt.axes([x + 0.55, y, 0.06, 0.05]), "ω2", initial=""),
            TextBox(plt.axes([x + 0.65, y, 0.06, 0.05]), "λ2", initial=""),
            Button(plt.axes([x + 0.73, y, 0.12, 0.05]), "Onda 2 ⥁"),
            RadioButtons(
                plt.axes([0.005, 0.5, 0.08, 0.1]),
                ("senoidal", "quadrada", "triangular", "serrada"),
            ),
            self.plot_2,
            self.result_plot,
        )

        self.figure.canvas.mpl_connect("key_press_event", self.on_press)

    # * Loop onde tudo é animado
    def animate(self, i):
        y_calcs = [
            plot.get_calc(self.get_timed_velocity(i, plot.lambda_))
            for plot in self.plots
        ]
        for i in range(len(self.lines)):
            # * atualiza os gráficos
            self.lines[i].set_ydata(y_calcs[i])
            # * atualiza o texto da parte direita do gráfico
            self.update_text(self.y_texts[i], y_calcs[i][-1])

        plt.draw()
        return [plot.line for plot in self.plots]

    # * Retorna a velocidade baseado no cumprimento da onda
    def get_timed_velocity(self, i, lambda_):
        if lambda_ == 0:
            return lambda_
        return i / lambda_

    # * Atualiza a posição e o valor do texto que aparece ao lado direito das ondas
    def update_text(self, y_text, input):
        y_text.set_text(f"{input:.2f}")
        y_text.set_position((y_text.get_position()[0], input))

    # * Ativa a função de pausar ao precionar enter
    def on_press(self, event):
        sys.stdout.flush()
        if event.key == "enter":
            self.toggle_pause()

    # * Função para pausar a animação
    def toggle_pause(self, *args, **kwargs):
        if self.paused:
            self.animation.resume()
        else:
            self.animation.pause()
        self.paused = not self.paused


Graph()
