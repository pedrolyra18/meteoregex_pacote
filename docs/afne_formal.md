# Descrição formal dos AFNε

> Documento gerado automaticamente por `ferramentas/gerar_documentacao.py`.

Cada autômato é uma quíntupla **A = (Q, Σ, δ, q₀, F)**. As transições são apresentadas na forma `δ(estado, símbolo) ∋ estado`, pois em um AFNε a função de transição devolve um *conjunto* de estados.

Classes de símbolos usadas nos rótulos (abreviações da união dos símbolos correspondentes):

- `⟨M⟩ = {A, B, ..., Z}  (abrevia [A-Z])`
- `⟨D⟩ = {0, 1, ..., 9}  (abrevia [0-9])`
- `⟨S⟩ = {+, -}          (abrevia [+-])`
- `⟨N⟩ = {1, 2, 3}       (abrevia [1-3])`

O símbolo `ε` indica movimento vazio: muda de estado sem consumir símbolo algum da entrada.


---

## ER-01

```
AFNε ER-01 — Código de estação meteorológica
Q  = {q0, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17}   (|Q| = 18)
Σ  = ⟨M⟩ = {A, B, ..., Z}  (abrevia [A-Z]), '-', ⟨D⟩ = {0, 1, ..., 9}  (abrevia [0-9]), '.'
q0 = q0
F  = {q12}
Movimentos vazios: 5
δ:
    δ(q0, ⟨M⟩) ∋ q1
    δ(q1, ⟨M⟩) ∋ q2
    δ(q2, -) ∋ q3
    δ(q3, ⟨M⟩) ∋ q4
    δ(q4, ⟨M⟩) ∋ q5
    δ(q5, ⟨M⟩) ∋ q6
    δ(q6, -) ∋ q7
    δ(q7, ⟨D⟩) ∋ q8
    δ(q8, ⟨D⟩) ∋ q9
    δ(q9, ⟨D⟩) ∋ q10
    δ(q10, ⟨M⟩) ∋ q11
    δ(q11, ε) ∋ q12
    δ(q11, ε) ∋ q13
    δ(q13, .) ∋ q14
    δ(q14, ⟨D⟩) ∋ q15
    δ(q15, ε) ∋ q16
    δ(q15, ⟨D⟩) ∋ q17
    δ(q17, ε) ∋ q16
    δ(q16, ε) ∋ q12
```


---

## ER-02

```
AFNε ER-02 — Carimbo temporal ISO-8601
Q  = {q0, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, q21, q22, q23, q24, q25, q26, q27, q28, q29, q30, q31, q32, q33, q34, q35, q36}   (|Q| = 37)
Σ  = ⟨D⟩ = {0, 1, ..., 9}  (abrevia [0-9]), '-', 'T', ':', '.', 'Z', ⟨S⟩ = {+, -}          (abrevia [+-])
q0 = q0
F  = {q27}
Movimentos vazios: 11
δ:
    δ(q0, ⟨D⟩) ∋ q1
    δ(q1, ⟨D⟩) ∋ q2
    δ(q2, ⟨D⟩) ∋ q3
    δ(q3, ⟨D⟩) ∋ q4
    δ(q4, -) ∋ q5
    δ(q5, ⟨D⟩) ∋ q6
    δ(q6, ⟨D⟩) ∋ q7
    δ(q7, -) ∋ q8
    δ(q8, ⟨D⟩) ∋ q9
    δ(q9, ⟨D⟩) ∋ q10
    δ(q10, T) ∋ q11
    δ(q11, ⟨D⟩) ∋ q12
    δ(q12, ⟨D⟩) ∋ q13
    δ(q13, :) ∋ q14
    δ(q14, ⟨D⟩) ∋ q15
    δ(q15, ⟨D⟩) ∋ q16
    δ(q16, :) ∋ q17
    δ(q17, ⟨D⟩) ∋ q18
    δ(q18, ⟨D⟩) ∋ q19
    δ(q19, ε) ∋ q20
    δ(q19, ε) ∋ q21
    δ(q21, .) ∋ q22
    δ(q22, ⟨D⟩) ∋ q23
    δ(q23, ε) ∋ q24
    δ(q23, ⟨D⟩) ∋ q25
    δ(q25, ε) ∋ q24
    δ(q25, ⟨D⟩) ∋ q26
    δ(q26, ε) ∋ q24
    δ(q24, ε) ∋ q20
    δ(q20, ε) ∋ q27
    δ(q20, ε) ∋ q28
    δ(q28, Z) ∋ q30
    δ(q30, ε) ∋ q29
    δ(q28, ⟨S⟩) ∋ q31
    δ(q31, ⟨D⟩) ∋ q32
    δ(q32, ⟨D⟩) ∋ q33
    δ(q33, :) ∋ q34
    δ(q34, ⟨D⟩) ∋ q35
    δ(q35, ⟨D⟩) ∋ q36
    δ(q36, ε) ∋ q29
    δ(q29, ε) ∋ q27
```


---

## ER-03

```
AFNε ER-03 — Leitura de sensor com unidade
Q  = {q0, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, q21, q22, q23, q24, q25, q26, q27, q28, q29}   (|Q| = 30)
Σ  = ⟨M⟩ = {A, B, ..., Z}  (abrevia [A-Z]), '=', ⟨S⟩ = {+, -}          (abrevia [+-]), ⟨D⟩ = {0, 1, ..., 9}  (abrevia [0-9]), '.', 'C', '%', 'm', 'h', 'P', 'a', '/', 's'
q0 = q0
F  = {q14}
Movimentos vazios: 19
δ:
    δ(q0, ⟨M⟩) ∋ q1
    δ(q1, ⟨M⟩) ∋ q2
    δ(q2, ⟨M⟩) ∋ q3
    δ(q3, ε) ∋ q4
    δ(q3, ⟨M⟩) ∋ q5
    δ(q5, ε) ∋ q4
    δ(q4, =) ∋ q6
    δ(q6, ε) ∋ q7
    δ(q6, ⟨S⟩) ∋ q8
    δ(q8, ε) ∋ q7
    δ(q7, ⟨D⟩) ∋ q9
    δ(q9, ε) ∋ q7
    δ(q9, ε) ∋ q10
    δ(q9, ε) ∋ q11
    δ(q11, .) ∋ q12
    δ(q12, ⟨D⟩) ∋ q13
    δ(q13, ε) ∋ q12
    δ(q13, ε) ∋ q10
    δ(q10, ε) ∋ q15
    δ(q15, C) ∋ q16
    δ(q16, ε) ∋ q14
    δ(q10, ε) ∋ q17
    δ(q17, %) ∋ q18
    δ(q18, ε) ∋ q14
    δ(q10, ε) ∋ q19
    δ(q19, m) ∋ q20
    δ(q20, m) ∋ q21
    δ(q21, ε) ∋ q14
    δ(q10, ε) ∋ q22
    δ(q22, h) ∋ q23
    δ(q23, P) ∋ q24
    δ(q24, a) ∋ q25
    δ(q25, ε) ∋ q14
    δ(q10, ε) ∋ q26
    δ(q26, m) ∋ q27
    δ(q27, /) ∋ q28
    δ(q28, s) ∋ q29
    δ(q29, ε) ∋ q14
```


---

## ER-04

```
AFNε ER-04 — Par de coordenadas geodésicas decimais
Q  = {q0, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, q21, q22, q23, q24, q25, q26, q27, q28, q29}   (|Q| = 30)
Σ  = ⟨S⟩ = {+, -}          (abrevia [+-]), ⟨D⟩ = {0, 1, ..., 9}  (abrevia [0-9]), '.', ','
q0 = q0
F  = {q27}
Movimentos vazios: 16
δ:
    δ(q0, ε) ∋ q1
    δ(q0, ⟨S⟩) ∋ q2
    δ(q2, ε) ∋ q1
    δ(q1, ⟨D⟩) ∋ q3
    δ(q3, ε) ∋ q4
    δ(q3, ⟨D⟩) ∋ q5
    δ(q5, ε) ∋ q4
    δ(q5, ⟨D⟩) ∋ q6
    δ(q6, ε) ∋ q4
    δ(q4, .) ∋ q7
    δ(q7, ⟨D⟩) ∋ q8
    δ(q8, ⟨D⟩) ∋ q9
    δ(q9, ⟨D⟩) ∋ q10
    δ(q10, ⟨D⟩) ∋ q11
    δ(q11, ε) ∋ q12
    δ(q11, ⟨D⟩) ∋ q13
    δ(q13, ε) ∋ q12
    δ(q13, ⟨D⟩) ∋ q14
    δ(q14, ε) ∋ q12
    δ(q12, ,) ∋ q15
    δ(q15, ε) ∋ q16
    δ(q15, ⟨S⟩) ∋ q17
    δ(q17, ε) ∋ q16
    δ(q16, ⟨D⟩) ∋ q18
    δ(q18, ε) ∋ q19
    δ(q18, ⟨D⟩) ∋ q20
    δ(q20, ε) ∋ q19
    δ(q20, ⟨D⟩) ∋ q21
    δ(q21, ε) ∋ q19
    δ(q19, .) ∋ q22
    δ(q22, ⟨D⟩) ∋ q23
    δ(q23, ⟨D⟩) ∋ q24
    δ(q24, ⟨D⟩) ∋ q25
    δ(q25, ⟨D⟩) ∋ q26
    δ(q26, ε) ∋ q27
    δ(q26, ⟨D⟩) ∋ q28
    δ(q28, ε) ∋ q27
    δ(q28, ⟨D⟩) ∋ q29
    δ(q29, ε) ∋ q27
```


---

## ER-05

```
AFNε ER-05 — Alerta hidrometeorológico
Q  = {q0, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20}   (|Q| = 21)
Σ  = '!', 'A', 'L', 'E', 'R', 'T', ':', 'N', 'I', 'V', ⟨N⟩ = {1, 2, 3}       (abrevia [1-3]), ⟨M⟩ = {A, B, ..., Z}  (abrevia [A-Z]), '_'
q0 = q0
F  = {q20}
Movimentos vazios: 5
δ:
    δ(q0, !) ∋ q1
    δ(q1, A) ∋ q2
    δ(q2, L) ∋ q3
    δ(q3, E) ∋ q4
    δ(q4, R) ∋ q5
    δ(q5, T) ∋ q6
    δ(q6, A) ∋ q7
    δ(q7, :) ∋ q8
    δ(q8, N) ∋ q9
    δ(q9, I) ∋ q10
    δ(q10, V) ∋ q11
    δ(q11, E) ∋ q12
    δ(q12, L) ∋ q13
    δ(q13, ⟨N⟩) ∋ q14
    δ(q14, :) ∋ q15
    δ(q15, ⟨M⟩) ∋ q16
    δ(q16, ε) ∋ q15
    δ(q16, ε) ∋ q17
    δ(q17, _) ∋ q18
    δ(q18, ⟨M⟩) ∋ q19
    δ(q19, ε) ∋ q18
    δ(q19, ε) ∋ q16
    δ(q16, ε) ∋ q20
```


---

## ER-06

```
AFNε ER-06 — Versão de firmware da estação
Q  = {q0, q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20, q21, q22, q23, q24, q25, q26, q27, q28, q29}   (|Q| = 30)
Σ  = 'f', 'w', '-', 'v', ⟨D⟩ = {0, 1, ..., 9}  (abrevia [0-9]), '.', 'a', 'l', 'p', 'h', 'b', 'e', 't', 'r', 'c'
q0 = q0
F  = {q10}
Movimentos vazios: 13
δ:
    δ(q0, f) ∋ q1
    δ(q1, w) ∋ q2
    δ(q2, -) ∋ q3
    δ(q3, v) ∋ q4
    δ(q4, ⟨D⟩) ∋ q5
    δ(q5, ε) ∋ q4
    δ(q5, .) ∋ q6
    δ(q6, ⟨D⟩) ∋ q7
    δ(q7, ε) ∋ q6
    δ(q7, .) ∋ q8
    δ(q8, ⟨D⟩) ∋ q9
    δ(q9, ε) ∋ q8
    δ(q9, ε) ∋ q10
    δ(q9, ε) ∋ q11
    δ(q11, -) ∋ q12
    δ(q12, ε) ∋ q14
    δ(q14, a) ∋ q15
    δ(q15, l) ∋ q16
    δ(q16, p) ∋ q17
    δ(q17, h) ∋ q18
    δ(q18, a) ∋ q19
    δ(q19, ε) ∋ q13
    δ(q12, ε) ∋ q20
    δ(q20, b) ∋ q21
    δ(q21, e) ∋ q22
    δ(q22, t) ∋ q23
    δ(q23, a) ∋ q24
    δ(q24, ε) ∋ q13
    δ(q12, ε) ∋ q25
    δ(q25, r) ∋ q26
    δ(q26, c) ∋ q27
    δ(q27, ε) ∋ q13
    δ(q13, .) ∋ q28
    δ(q28, ⟨D⟩) ∋ q29
    δ(q29, ε) ∋ q28
    δ(q29, ε) ∋ q10
```
