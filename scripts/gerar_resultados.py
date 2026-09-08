"""Gera tabelas e gráficos dos Exercícios 1.1 e 1.2."""

from __future__ import annotations

import argparse
import csv
import html
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.disponibilidade import (  # noqa: E402
    disponibilidade_analitica,
    disponibilidade_simulada,
    k_maioria,
)


N_VALUES = (4, 8, 12, 16, 20)
P_VALUES = (0.50, 0.70, 0.80, 0.90, 0.95, 0.99)


def casos(n: int) -> tuple[tuple[str, int], ...]:
    return (
        ("consulta (k=1)", 1),
        ("maioria (k=ceil(n/2))", k_maioria(n)),
        ("atualizacao (k=n)", n),
    )


def gerar_linhas(rodadas: int, seed: int) -> list[dict[str, object]]:
    linhas: list[dict[str, object]] = []
    for n in N_VALUES:
        for p in P_VALUES:
            for nome_caso, k in casos(n):
                analitica = disponibilidade_analitica(n, k, p)
                experimental, sucessos = disponibilidade_simulada(
                    n, k, p, rodadas=rodadas, seed=seed + n * 10_000 + int(p * 100),
                )
                linhas.append(
                    {
                        "n": n,
                        "k": k,
                        "caso": nome_caso,
                        "p": p,
                        "disponibilidade_analitica": analitica,
                        "disponibilidade_experimental": experimental,
                        "sucessos": sucessos,
                        "rodadas": rodadas,
                        "erro_absoluto": abs(experimental - analitica),
                    }
                )
    return linhas


def escrever_csv(caminho: Path, linhas: list[dict[str, object]], colunas: list[str]) -> None:
    with caminho.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()
        escritor.writerows(linhas)


def _svg_text(texto: str) -> str:
    return html.escape(str(texto), quote=True)


def _polyline(points: list[tuple[float, float]], color: str, dashed: bool = False) -> str:
    pontos = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
    extra = ' stroke-dasharray="7 5"' if dashed else ""
    return f'<polyline points="{pontos}" fill="none" stroke="{color}" stroke-width="2.2"{extra}/>'


def _svg_base(title: str, width: int = 1500, height: int = 560) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="titulo">',
        f'<title id="titulo">{_svg_text(title)}</title>',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="{width / 2:.0f}" y="30" text-anchor="middle" font-family="Arial" font-size="22" fill="#222">{_svg_text(title)}</text>',
    ]


def _desenhar_eixos(svg: list[str], x0: float, y0: float, largura: float, altura: float, titulo: str, xmin: float, xmax: float) -> None:
    svg.append(f'<text x="{x0 + largura / 2:.0f}" y="{y0 - 12:.0f}" text-anchor="middle" font-family="Arial" font-size="16" fill="#222">{_svg_text(titulo)}</text>')
    for valor in np.linspace(0, 1, 6):
        y = y0 + altura * (1 - valor)
        svg.append(f'<line x1="{x0:.2f}" y1="{y:.2f}" x2="{x0 + largura:.2f}" y2="{y:.2f}" stroke="#dddddd"/>')
        svg.append(f'<text x="{x0 - 10:.2f}" y="{y + 5:.2f}" text-anchor="end" font-family="Arial" font-size="12" fill="#444">{valor:.1f}</text>')
    for valor in np.linspace(xmin, xmax, 6):
        x = x0 + largura * ((valor - xmin) / (xmax - xmin))
        svg.append(f'<line x1="{x:.2f}" y1="{y0:.2f}" x2="{x:.2f}" y2="{y0 + altura:.2f}" stroke="#eeeeee"/>')
        svg.append(f'<text x="{x:.2f}" y="{y0 + altura + 20:.2f}" text-anchor="middle" font-family="Arial" font-size="12" fill="#444">{valor:.2f}</text>')
    svg.append(f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{largura:.2f}" height="{altura:.2f}" fill="none" stroke="#555"/>')
    svg.append(f'<text x="{x0 + largura / 2:.0f}" y="{y0 + altura + 43:.0f}" text-anchor="middle" font-family="Arial" font-size="13" fill="#333">Probabilidade individual p</text>')
    svg.append(f'<text x="{x0 - 55:.0f}" y="{y0 + altura / 2:.0f}" text-anchor="middle" transform="rotate(-90 {x0 - 55:.0f},{y0 + altura / 2:.0f})" font-family="Arial" font-size="13" fill="#333">Disponibilidade</text>')


def _ponto(x: float, y: float, x0: float, y0: float, largura: float, altura: float, xmin: float, xmax: float) -> tuple[float, float]:
    return x0 + largura * ((x - xmin) / (xmax - xmin)), y0 + altura * (1 - y)


def gerar_grafico_analitico(pasta: Path) -> None:
    svg = _svg_base("Disponibilidade analítica para diferentes réplicas")
    cores = ["#440154", "#3b528b", "#21918c", "#5ec962", "#fde725"]
    p_values = np.linspace(0.0, 1.0, 101)
    for indice, (nome_caso, _) in enumerate(casos(20)):
        x0, y0, largura, altura = 90 + indice * 465, 85, 360, 360
        _desenhar_eixos(svg, x0, y0, largura, altura, nome_caso, 0, 1)
        for n, cor in zip(N_VALUES, cores):
            k = dict(casos(n))[nome_caso]
            pontos = [_ponto(float(p), disponibilidade_analitica(n, k, float(p)), x0, y0, largura, altura, 0, 1) for p in p_values]
            svg.append(_polyline(pontos, cor))
    for indice, n in enumerate(N_VALUES):
        x = 1190 + (indice % 2) * 105
        y = 105 + (indice // 2) * 28
        svg.append(f'<line x1="{x}" y1="{y}" x2="{x + 22}" y2="{y}" stroke="{cores[indice]}" stroke-width="3"/>')
        svg.append(f'<text x="{x + 30}" y="{y + 5}" font-family="Arial" font-size="13" fill="#333">n={n}</text>')
    svg.append('</svg>')
    (pasta / "disponibilidade_analitica.svg").write_text("\n".join(svg), encoding="utf-8")


def gerar_grafico_comparacao(pasta: Path, linhas: list[dict[str, object]]) -> None:
    n_escolhido = 12
    svg = _svg_base(f"Teoria x simulação — n={n_escolhido}")
    for indice, (nome_caso, _) in enumerate(casos(n_escolhido)):
        x0, y0, largura, altura = 90 + indice * 465, 85, 360, 360
        _desenhar_eixos(svg, x0, y0, largura, altura, nome_caso, 0.5, 1)
        dados = [linha for linha in linhas if linha["n"] == n_escolhido and linha["caso"] == nome_caso]
        dados.sort(key=lambda linha: float(linha["p"]))
        pontos_analiticos = [_ponto(float(linha["p"]), float(linha["disponibilidade_analitica"]), x0, y0, largura, altura, 0.5, 1) for linha in dados]
        pontos_experimentais = [_ponto(float(linha["p"]), float(linha["disponibilidade_experimental"]), x0, y0, largura, altura, 0.5, 1) for linha in dados]
        svg.append(_polyline(pontos_analiticos, "#1f77b4"))
        svg.append(_polyline(pontos_experimentais, "#d62728", dashed=True))
        for x, y in pontos_experimentais:
            svg.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.5" fill="#d62728"/>')
    svg.append('<line x1="1190" y1="105" x2="1215" y2="105" stroke="#1f77b4" stroke-width="3"/>')
    svg.append('<text x="1225" y="110" font-family="Arial" font-size="13" fill="#333">Analítica</text>')
    svg.append('<line x1="1190" y1="135" x2="1215" y2="135" stroke="#d62728" stroke-width="3" stroke-dasharray="7 5"/>')
    svg.append('<text x="1225" y="140" font-family="Arial" font-size="13" fill="#333">Experimental</text>')
    svg.append('</svg>')
    (pasta / "teoria_vs_simulacao.svg").write_text("\n".join(svg), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rodadas", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--saida", type=Path, default=ROOT / "resultados")
    args = parser.parse_args()
    if args.rodadas <= 0:
        parser.error("--rodadas deve ser maior que zero")

    args.saida.mkdir(parents=True, exist_ok=True)
    linhas = gerar_linhas(args.rodadas, args.seed)
    colunas = [
        "n", "k", "caso", "p", "disponibilidade_analitica",
        "disponibilidade_experimental", "sucessos", "rodadas", "erro_absoluto",
    ]
    escrever_csv(args.saida / "comparacao_simulacao.csv", linhas, colunas)

    analiticas = []
    for n in N_VALUES:
        for p in P_VALUES:
            for nome_caso, k in casos(n):
                analiticas.append(
                    {"n": n, "k": k, "caso": nome_caso, "p": p,
                     "disponibilidade_analitica": disponibilidade_analitica(n, k, p)}
                )
    escrever_csv(
        args.saida / "disponibilidade.csv",
        analiticas,
        ["n", "k", "caso", "p", "disponibilidade_analitica"],
    )
    gerar_grafico_analitico(args.saida)
    gerar_grafico_comparacao(args.saida, linhas)
    print(f"Resultados gravados em: {args.saida}")


if __name__ == "__main__":
    main()
