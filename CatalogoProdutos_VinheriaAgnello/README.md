# Sistema de Microsserviços: Produtos + Inventário (Vinhos)

Este projeto utiliza dois microsserviços simples para demonstrar comunicação interna em um ambiente com **Docker**, **DNS interno via rede do Docker** e **Consul** para **descoberta de serviços**.

## 1. Microsserviços

### Serviço: **Products API**

Responsável por cadastrar e listar produtos.

Endpoints principais:

* `GET /v1/products` – lista todos os produtos
* `GET /v1/products/{id}` – obtém produto por ID
* `POST /v1/products` – cria um novo produto
* `PUT /v1/products/{id}` – atualiza um produto existente
* `GET /v1/products/{id}/stock` – consulta o serviço de Inventário para saber o estoque do produto

Esse serviço acessa o **Inventory API** chamando:

```
http://inventory/v1/inventory/{product_id}
```

---

### Serviço: **Inventory API (Vinhos)**

Responsável pelo controle de **estoque**, **lotes**, **validades** e **reservas**.

Endpoints:

| Método | Endpoint                             | Função                                                                  |
| ------ | ------------------------------------ | ----------------------------------------------------------------------- |
| GET    | `/v1/inventory/{product_id}`         | Retorna **estoque total livre** (somando todos os lotes não reservados) |
| GET    | `/v1/inventory/{product_id}/batches` | Lista todos os lotes detalhadamente                                     |
| POST   | `/v1/inventory/{product_id}/batches` | Adiciona lote ao receber nova remessa                                   |
| POST   | `/v1/inventory/{product_id}/reserve` | Reserva unidades (sem remover do estoque)                               |
| POST   | `/v1/inventory/{product_id}/release` | Libera uma reserva previamente feita                                    |
| POST   | `/v1/inventory/{product_id}/consume` | Remove unidades definitivamente (ex: venda concluída)                   |

Banco interno (apenas para demonstração):

```
INVENTORY_DB = {
  product_id: {
    "batches": [ { "batch_id", "qty", "expires_at" } ],
    "reserved": numero_total_reservado
  }
}
```

---

## 2. Consul – Descoberta de Serviços

O **Consul** está rodando em um container e registra os serviços `product-service` e `inventory-service`.

Acesse a interface Web para ver os serviços registrados:

```
http://localhost:8500
```

Você deverá ver algo assim:

```
product-service - passing
inventory-service - passing
```

Caso veja `critical`, verifique a URL de healthcheck configurada no registro.

---

## 3. Rede e DNS (Simulação do DHCP/DNS do Windows Server)

O Docker cria automaticamente uma **rede interna** onde cada container recebe um **nome DNS**.

```
product-service → http://products
inventory-service → http://inventory
consul → http://consul
```

Não é necessário configurar IP. Os serviços se comunicam **pelo nome do container**.

Isso simula **DNS interno**.

O DHCP é implicitamente simulado porque o Docker atribui IP automaticamente.

---

## 4. Como Rodar

Na pasta do projeto:

```
docker compose up --build
```

Aguardar logs e então testar:

```
curl http://localhost/v1/products
```

Ou acessar pelo navegador:

```
http://localhost/docs
http://inventory/docs
```

---

## 5. Demonstração da Comunicação Entre Serviços

Quando você faz:

```
GET /v1/products/{id}/stock
```

O Products API faz internamente:

```
GET http://inventory/v1/inventory/{id}
```

Ou seja: **um serviço chamando outro usando DNS interno + Consul.**

---

## 6. Como isso atende ao Trabalho

| Requisito             | Atendido? | Como?                                         |
| --------------------- | --------- | --------------------------------------------- |
| 2 microsserviços      | ✅         | Products API + Inventory API                  |
| Rede simulada         | ✅         | Docker network cria rede interna              |
| DHCP Simulado         | ✅         | Docker gerencia IP automático                 |
| DNS Simulado          | ✅         | Containers acessam via nome (ex: `inventory`) |
| Serviços se comunicam | ✅         | Products chama Inventory via HTTP interno     |
| Registro de serviços  | ✅         | Consul lista e monitora cada serviço          |

---
