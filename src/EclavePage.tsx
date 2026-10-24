import React, { useState } from 'react';
import './eclave.css';

// Página de oferta ECLAVE — implementada a partir do Figma "PÁGINA ECLAVE" (node 46:6)
const asset = (name: string) => `${process.env.PUBLIC_URL}/eclave/${name}`;

const photos = {
  principal: asset('foto-principal.png'),
  i03: asset('foto-i03.png'),
  i05: asset('foto-i05.png'),
  i09: asset('foto-i09.png'),
  i10: asset('foto-i10.png'),
  i14: asset('foto-i14.png'),
  i18: asset('foto-i18.png'),
  i21: asset('foto-i21.png'),
};

const galleryPhotos = [photos.principal, photos.i05, photos.i10, photos.i09, photos.i14];

interface Kit {
  id: number;
  name: string;
  badge: string;
  badgeClass: string;
  description: string;
  oldPrice: number;
  price: number;
}

const kits: Kit[] = [
  { id: 1, name: '1 frasco', badge: 'EXPERIMENTE', badgeClass: 'ec-badge--peach', description: 'Tratamento de 1 mês', oldPrice: 179.9, price: 129.9 },
  { id: 2, name: '2 frascos', badge: 'MAIS VENDIDO', badgeClass: '', description: 'Tratamento de 2 meses · R$ 123,95 cada', oldPrice: 359.8, price: 247.9 },
  { id: 3, name: '3 frascos', badge: 'MELHOR OFERTA', badgeClass: 'ec-badge--wine', description: 'Tratamento de 3 meses · R$ 122,63 cada + brinde nécessaire', oldPrice: 539.7, price: 367.9 },
];

const kitCards = [
  { kitId: 1, title: 'Kit 1 ECLAVE', sub: 'Tratamento de 1 mês', photo: photos.i10, discount: '-28%', freeShipping: false },
  { kitId: 2, title: 'Kit 2 ECLAVE', sub: 'Tratamento de 2 meses', photo: photos.i03, discount: '-31%', freeShipping: true },
  { kitId: 3, title: 'Kit 3 ECLAVE + nécessaire', sub: 'Tratamento de 3 meses', photo: photos.i21, discount: '-32%', freeShipping: true },
];

const solutions = [
  { title: 'Seca as espinhas', text: 'Reduz a acne ativa e acalma a inflamação, sem ressecar a pele.' },
  { title: 'Previne novas espinhas', text: 'Desobstrui os poros e equilibra a oleosidade dia após dia.' },
  { title: 'Clareia manchas', text: 'Atua na melanina e devolve um tom mais uniforme ao rosto.' },
  { title: 'Suaviza marcas de acne', text: 'Acelera a recuperação das marcas escuras e avermelhadas que as espinhas deixam.' },
  { title: 'Controla a oleosidade', text: 'Pele com menos brilho e poros visivelmente menores.' },
  { title: 'Uniformiza textura e tom', text: 'Pele mais lisa, firme e iluminada a cada aplicação.' },
];

const steps = [
  { label: 'PASSO 01', title: 'Limpe a pele', text: 'Lave o rosto com um sabonete suave e seque com cuidado.', photo: photos.i14 },
  { label: 'PASSO 02', title: 'Aplique o ECLAVE', text: 'Aplique 3 a 4 gotas do sérum e espalhe por todo o rosto até a completa absorção.', photo: photos.i09 },
  { label: 'PASSO 03', title: 'Use 2x ao dia', text: 'Manhã e noite. De dia, finalize sempre com protetor solar.', photo: photos.i10 },
];

const actives = [
  { sigla: 'Pep', name: 'Peptídeos', tag: 'TEXTURA', tagClass: 'ec-badge--gold-dark', text: 'Estimulam a renovação e o colágeno, deixando a pele mais lisa e firme.' },
  { sigla: 'DNA', name: 'PDRN (DNA de salmão)', tag: 'ACNE', tagClass: 'ec-badge--black', text: 'Regenera a pele e acelera a recuperação das marcas deixadas pela acne.' },
  { sigla: 'Ret', name: 'Retinaldeído', tag: 'ACNE', tagClass: 'ec-badge--black', text: 'Renova as células, desobstrui os poros e reduz espinhas e cravos.' },
  { sigla: 'Cica', name: 'Centella asiática', tag: 'ACNE', tagClass: 'ec-badge--black', text: 'Acalma a vermelhidão e a inflamação da pele com acne.', small: true },
  { sigla: 'Arb', name: 'Alfa-arbutin', tag: 'MANCHAS', tagClass: '', text: 'Clareia manchas reduzindo a produção de melanina, sem agredir a pele.' },
  { sigla: 'TXA', name: 'Ácido tranexâmico', tag: 'MANCHAS', tagClass: '', text: 'Uniformiza o tom e atua nas manchas mais teimosas e no melasma.' },
  { sigla: 'Cu', name: 'Copper peptide', tag: 'TEXTURA', tagClass: 'ec-badge--gold-dark', text: 'Reparação e firmeza: ajuda a pele a se recuperar mais rápido.' },
];

const results = [
  'sentiram menos espinhas',
  'viram as manchas mais claras',
  'notaram menos oleosidade',
  'sentiram a pele mais lisa',
  'perceberam o tom mais uniforme',
  'recomendariam a ECLAVE',
];

const reviewFilters = ['Mais recentes', 'Com fotos', 'Só texto', 'Melhor avaliadas'];

const reviews = [
  { hasPhotos: true },
  { hasPhotos: false },
  { hasPhotos: true },
  { hasPhotos: false },
];

const instagramPhotos = [photos.principal, photos.i05, photos.i14, photos.i03, photos.i10, photos.i18, photos.i09, photos.i21];

const faqs = [
  {
    q: 'Em quanto tempo vejo resultado?',
    a: 'A textura e a oleosidade mudam nas primeiras semanas. Manchas pedem uso contínuo: o ideal é seguir o tratamento por 60 a 90 dias.',
  },
  { q: 'A ECLAVE é regularizada na Anvisa?', a: 'Resposta a preencher.' },
  { q: 'Serve para pele oleosa e com acne?', a: 'Resposta a preencher.' },
  { q: 'Posso usar junto com outros ácidos ou retinol?', a: 'Resposta a preencher.' },
  { q: 'Grávidas e lactantes podem usar?', a: 'Resposta a preencher.' },
  { q: 'O site é seguro?', a: 'Resposta a preencher.' },
  { q: 'O frete é grátis?', a: 'Resposta a preencher.' },
  { q: 'Qual o prazo de entrega?', a: 'Resposta a preencher.' },
  { q: 'E se eu não gostar?', a: 'Resposta a preencher.' },
];

const formatBRL = (value: number) =>
  value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }).replace(/ /g, ' ');

// Parcela arredondada para cima ao centavo (R$ 247,90 → 12x de R$ 20,66)
const installment = (value: number) => Math.ceil(Math.round(value * 100) / 12) / 100;

const scrollToBuy = () => {
  document.getElementById('comprar')?.scrollIntoView({ behavior: 'smooth' });
};

function Cta({ label = 'EU QUERO MEU ECLAVE', full, onClick = scrollToBuy }: { label?: string; full?: boolean; onClick?: () => void }) {
  return (
    <button type="button" className={`ec-cta${full ? ' ec-cta--full' : ''}`} onClick={onClick}>
      <span className="ec-cta__label">{label}</span>
      <span>→</span>
    </button>
  );
}

function Bullet({ icon, size, light, children }: { icon: string; size: number; light?: boolean; children: React.ReactNode }) {
  return (
    <div className={`ec-bullet${light ? ' ec-bullet--light' : ''}`}>
      <img src={icon} alt="" width={size} height={size} />
      <span>{children}</span>
    </div>
  );
}

function EclavePage() {
  const [selectedKit, setSelectedKit] = useState(2);
  const [activePhoto, setActivePhoto] = useState(0);
  const [cartCount, setCartCount] = useState(0);
  const [cep, setCep] = useState('');
  const [shippingMessage, setShippingMessage] = useState('');
  const [reviewFilter, setReviewFilter] = useState(reviewFilters[0]);
  const [openFaq, setOpenFaq] = useState<number | null>(0);

  const kit = kits.find(k => k.id === selectedKit) ?? kits[1];

  const addToCart = (kitId: number) => {
    setSelectedKit(kitId);
    setCartCount(count => count + 1);
  };

  const handleCep = (value: string) => {
    const digits = value.replace(/\D/g, '').slice(0, 8);
    setCep(digits.length > 5 ? `${digits.slice(0, 5)}-${digits.slice(5)}` : digits);
    setShippingMessage('');
  };

  const calculateShipping = () => {
    if (cep.replace(/\D/g, '').length !== 8) {
      setShippingMessage('Digite um CEP válido com 8 números.');
      return;
    }
    setShippingMessage(
      selectedKit > 1
        ? 'Frete grátis para este kit.'
        : 'O valor do frete para o seu CEP aparece no checkout. Nos kits, o frete é grátis.'
    );
  };

  const visibleReviews = reviews.filter(r => {
    if (reviewFilter === 'Com fotos') return r.hasPhotos;
    if (reviewFilter === 'Só texto') return !r.hasPhotos;
    return true;
  });

  return (
    <div className="ec">
      {/* 00 · Barra de oferta */}
      <div className="ec-topbar">
        <span>HOJE: ATÉ 32% OFF</span>
        <span className="ec-dot">•</span>
        <span>FRETE GRÁTIS NOS KITS</span>
        <span className="ec-dot">•</span>
        <span>12X SEM JUROS</span>
      </div>

      {/* 01 · Header */}
      <header className="ec-header">
        <div className="ec-container">
          <nav className="ec-menu">
            <a href="#inicio">Início</a>
            <a href="#comprar">Produtos</a>
            <a href="#rastreio">Rastreio</a>
            <a href="#duvidas">Dúvidas</a>
          </nav>
          <div className="ec-logo" id="inicio">
            <span className="ec-logo__name">ECLAVE</span>
            <span className="ec-logo__sub">SKIN</span>
          </div>
          <div className="ec-header__actions">
            <label className="ec-search">
              <input type="search" placeholder="Buscar produto" aria-label="Buscar produto" />
              <img src={asset('icon-search.svg')} alt="" width={20} height={20} />
            </label>
            <button type="button" className="ec-cart" aria-label={`Carrinho com ${cartCount} itens`}>
              <img src={asset('icon-cart.svg')} alt="" width={28} height={28} />
              <span className="ec-cart__count">{cartCount}</span>
            </button>
          </div>
        </div>
      </header>

      {/* 02 · Produto (área de compra) */}
      <section className="ec-product" id="comprar">
        <div className="ec-container">
          <p className="ec-breadcrumb">{'Início  ›  Loja  ›  Sérum Clareador Noturno ECLAVE 30 ml'}</p>
          <div className="ec-product__cols">
            <div className="ec-gallery">
              <div className="ec-gallery__main">
                <img src={galleryPhotos[activePhoto]} alt="Sérum Clareador Noturno ECLAVE" />
                <span className="ec-badge">-32% OFF</span>
                <span className="ec-badge ec-badge--peach">FRETE GRÁTIS</span>
              </div>
              <div className="ec-thumbs">
                {galleryPhotos.map((src, index) => (
                  <button
                    key={src}
                    type="button"
                    className={`ec-thumb${index === activePhoto ? ' ec-thumb--active' : ''}`}
                    onClick={() => setActivePhoto(index)}
                    aria-label={`Ver foto ${index + 1}`}
                  >
                    <img src={src} alt="" />
                  </button>
                ))}
              </div>
            </div>

            <div className="ec-buy">
              <div className="ec-rating">
                <span className="ec-stars">★★★★★</span>
                <span className="ec-rating__text">{'4,9  ·  (000 avaliações)'}</span>
              </div>
              <h1>
                Sérum Clareador Noturno <em>ECLAVE</em> 30 ml
              </h1>
              <p className="ec-buy__desc">
                Um sérum noturno com 7 ativos coreanos, criado para mulheres que querem tratar a acne, clarear as manchas e uniformizar o tom e a textura do rosto. Tudo num só frasco.
              </p>
              <div className="ec-bullets">
                <Bullet icon={asset('icon-check.svg')} size={18}>Seca e previne a acne</Bullet>
                <Bullet icon={asset('icon-check.svg')} size={18}>Clareia manchas e marcas de espinha</Bullet>
                <Bullet icon={asset('icon-check.svg')} size={18}>Uniformiza o tom e a textura do rosto</Bullet>
              </div>
              <div className="ec-divider" />
              <p className="ec-buy__label">Escolha o seu tratamento:</p>
              <div className="ec-kits" role="radiogroup" aria-label="Escolha o seu tratamento">
                {kits.map(k => {
                  const selected = k.id === selectedKit;
                  return (
                    <button
                      key={k.id}
                      type="button"
                      role="radio"
                      aria-checked={selected}
                      className={`ec-kit${selected ? ' ec-kit--selected' : ''}`}
                      onClick={() => setSelectedKit(k.id)}
                    >
                      <img src={asset(selected ? 'icon-radio-on.svg' : 'icon-radio.svg')} alt="" width={22} height={22} />
                      <span className="ec-kit__info">
                        <span className="ec-kit__line">
                          <span className="ec-kit__name">{k.name}</span>
                          <span className={`ec-badge ec-badge--sm ${k.badgeClass}`}>{k.badge}</span>
                        </span>
                        <span className="ec-kit__desc">{k.description}</span>
                      </span>
                      <span className="ec-kit__price">
                        <span className="ec-old-price">{formatBRL(k.oldPrice)}</span>
                        <strong>{formatBRL(k.price)}</strong>
                      </span>
                    </button>
                  );
                })}
              </div>
              <div className="ec-summary">
                <span className="ec-summary__price">{formatBRL(kit.price)}</span>
                <span className="ec-summary__parcelas">
                  <span>ou 12x de {formatBRL(installment(kit.price))} sem juros</span>
                  <span>Você economiza {formatBRL(kit.oldPrice - kit.price)}</span>
                </span>
              </div>
              <Cta label="COMPRAR AGORA" full onClick={() => addToCart(selectedKit)} />
              <div className="ec-trust">
                <div className="ec-trust__item">
                  <img src={asset('icon-shield.svg')} alt="" width={24} height={24} />
                  Compra 100% segura
                </div>
                <div className="ec-trust__item">
                  <img src={asset('icon-truck.svg')} alt="" width={24} height={24} />
                  Frete grátis nos kits
                </div>
                <div className="ec-trust__item">
                  <img src={asset('icon-guarantee.svg')} alt="" width={24} height={24} />
                  Garantia de 7 dias
                </div>
              </div>
              <div className="ec-shipping">
                <label htmlFor="ec-cep">Calcular frete</label>
                <input
                  id="ec-cep"
                  inputMode="numeric"
                  placeholder="Digite seu CEP"
                  value={cep}
                  onChange={e => handleCep(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && calculateShipping()}
                />
                <button type="button" onClick={calculateShipping}>OK</button>
              </div>
              {shippingMessage && <p className="ec-shipping__result">{shippingMessage}</p>}
              <p className="ec-payments">{'Pix  ·  Cartão em até 12x  ·  Boleto'}</p>
            </div>
          </div>
        </div>
      </section>

      {/* 03 · Eficácia */}
      <section className="ec-section" style={{ background: '#fff' }}>
        <div className="ec-container ec-split">
          <div className="ec-photo" style={{ width: 540, height: 620 }}>
            <img src={photos.i14} alt="Mulher sorrindo com a pele uniforme" />
          </div>
          <div className="ec-split__text">
            <p className="ec-eyebrow">EFICÁCIA</p>
            <h2 className="ec-title">A solução definitiva contra <em>acne e manchas</em></h2>
            <p className="ec-body">
              Diga adeus às espinhas e às manchas que roubam a sua confiança. O Sérum Clareador ECLAVE foi criado para mulheres que querem tratar a acne, clarear as marcas e uniformizar o tom do rosto, sem precisar de uma rotina com dez passos.
            </p>
            <p className="ec-body">
              Com tecnologia coreana e 7 ativos que trabalham em conjunto, ele trata sem agredir e devolve a pele lisa, uniforme e iluminada. Um cuidado noturno, delicado e eficaz, feito para quem não quer mais esconder o rosto atrás da base.
            </p>
            <div className="ec-mini-grid">
              {[
                ['Reduz a acne', 'Controla a oleosidade e as espinhas'],
                ['Clareia manchas', 'Atua nas marcas e no tom irregular'],
                ['Uniformiza', 'Pele mais lisa e alinhada'],
                ['Testado', 'Dermatologicamente testado'],
              ].map(([title, text]) => (
                <div className="ec-mini" key={title}>
                  <strong>{title}</strong>
                  <span>{text}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* 04 · Tecnologia coreana */}
      <section className="ec-section" style={{ background: '#5b2a33' }}>
        <div className="ec-container ec-split">
          <div className="ec-split__text">
            <p className="ec-eyebrow ec-eyebrow--gold">TECNOLOGIA COREANA</p>
            <h2 className="ec-title ec-title--light">7 ativos coreanos em <em>um só frasco.</em></h2>
            <p className="ec-body ec-body--light ec-body--18">
              Você está diante de um sérum que reúne, num só frasco, ativos que normalmente estariam em três ou quatro produtos diferentes. A gente não seguiu uma tendência. A gente criou uma chave.
            </p>
            <p className="ec-body ec-body--light ec-body--18">
              Acne, manchas e textura irregular têm causas diferentes. Por isso, tratar só uma delas não resolve: a espinha passa, mas a marca fica.
            </p>
            <p className="ec-body ec-body--light ec-body--18">
              Foi assim que nasceu a ECLAVE: peptídeos, PDRN, retinaldeído, centella asiática, alfa-arbutin, ácido tranexâmico e copper peptide trabalhando juntos, todas as noites, enquanto você dorme.
            </p>
            <p className="ec-body ec-body--light ec-body--18">
              O resultado? Um tratamento completo para acne, manchas, textura e tom, com a delicadeza que a sua pele merece.
            </p>
            <div className="ec-outline-badges">
              <span className="ec-outline-badge">TECNOLOGIA COREANA</span>
              <span className="ec-outline-badge">EMBALAGEM JOIA</span>
              <span className="ec-outline-badge">DERMATOLOGICAMENTE TESTADO</span>
            </div>
          </div>
          <div className="ec-photo" style={{ width: 520, height: 680 }}>
            <img src={photos.i05} alt="Frasco do sérum ECLAVE" />
          </div>
        </div>
      </section>

      {/* 05 · Liberdade (acne) */}
      <section className="ec-section" style={{ background: '#fbf4ec' }}>
        <div className="ec-container ec-split ec-split--72">
          <div className="ec-split__text">
            <p className="ec-eyebrow">LIBERDADE</p>
            <h2 className="ec-title">Dê adeus às <em>espinhas</em> e à vergonha de sair sem base</h2>
            <p className="ec-body">
              Você evita foto de perto? Passa a mão no rosto o tempo todo para conferir se nasceu mais uma espinha? Sente vergonha de sair de cara lavada? Você não está sozinha.
            </p>
            <p className="ec-body">
              A acne adulta é mais comum do que parece: oleosidade, hormônios e estresse entopem os poros e inflamam a pele. A ECLAVE chegou para mudar essa realidade. Com retinaldeído e centella asiática, ela desobstrui os poros, acalma a inflamação e devolve a sua liberdade de mostrar o rosto. Sem filtro, sem medo.
            </p>
          </div>
          <div className="ec-before-after">
            <div className="ec-before-after__photos">
              <div className="ec-placeholder">
                <span className="ec-badge ec-badge--black">ANTES</span>
                foto real<br />de cliente
              </div>
              <div className="ec-placeholder">
                <span className="ec-badge">DEPOIS</span>
                foto real<br />de cliente
              </div>
            </div>
            <p className="ec-before-after__caption">Acne ativa · 30 dias de uso</p>
          </div>
        </div>
      </section>

      {/* 06 · Liberte-se (manchas e marcas) */}
      <section className="ec-section" style={{ background: '#f7e6dc' }}>
        <div className="ec-container ec-split">
          <div className="ec-photo" style={{ width: 520, height: 640 }}>
            <img src={photos.i10} alt="Mão segurando o sérum ECLAVE" />
          </div>
          <div className="ec-split__text">
            <p className="ec-eyebrow">LIBERTE-SE</p>
            <h2 className="ec-title">Marcas de espinha? Diga adeus às <em>manchas</em> que a acne deixou</h2>
            <p className="ec-body">
              A espinha some, mas a marca escura fica por semanas, às vezes meses. E quanto mais você mexe, mais ela demora a sair. Você não está sozinha: as manchas pós-acne estão entre as maiores queixas de quem já teve espinhas.
            </p>
            <p className="ec-body">
              A ECLAVE foi desenvolvida com alfa-arbutin e ácido tranexâmico, ativos reconhecidos pela ação clareadora, e com PDRN, que acelera a recuperação da pele. Juntos, eles clareiam as marcas e uniformizam o tom sem agredir.
            </p>
            <p className="ec-body">
              Um cuidado noturno para devolver o tom natural, o toque macio e a confiança que você merece.
            </p>
          </div>
        </div>
      </section>

      {/* 07 · Pele de vidro */}
      <section className="ec-section" style={{ background: '#fff' }}>
        <div className="ec-container ec-split">
          <div className="ec-split__text">
            <p className="ec-eyebrow">PELE DE VIDRO</p>
            <h2 className="ec-title">Poros abertos e oleosidade? A ECLAVE trata com <em>ciência e delicadeza</em></h2>
            <p className="ec-body">
              Brilho no meio da tarde, poros dilatados e textura irregular? Com peptídeos e copper peptide, a ECLAVE estimula a renovação da pele, controla a oleosidade e deixa o rosto mais liso, firme e uniforme.
            </p>
            <p className="ec-body">Resultado visível com um cuidado simples: algumas gotas, toda noite.</p>
            <Cta label="QUERO MEU ECLAVE" />
          </div>
          <div className="ec-photo" style={{ width: 520, height: 600 }}>
            <img src={photos.i09} alt="Conta-gotas do sérum ECLAVE" />
          </div>
        </div>
      </section>

      {/* 08 · 6 soluções em um frasco */}
      <section className="ec-section" style={{ background: '#fbf4ec' }}>
        <div className="ec-container ec-center-head">
          <p className="ec-eyebrow">O MAIS COMPLETO DO MERCADO</p>
          <h2 className="ec-title">Com apenas um frasco, entregamos <em>6 soluções</em> para a sua pele</h2>
          <div className="ec-banner">
            <img src={photos.i03} alt="Caixas do sérum ECLAVE" />
          </div>
          <div className="ec-grid-3">
            {solutions.map((s, index) => (
              <div className="ec-solution" key={s.title}>
                <span className="ec-num">{String(index + 1).padStart(2, '0')}</span>
                <div className="ec-solution__text">
                  <p className="ec-card-title">{s.title}</p>
                  <p className="ec-card-text">{s.text}</p>
                </div>
              </div>
            ))}
          </div>
          <div className="ec-special">
            <p className="ec-eyebrow ec-eyebrow--gold">ATENÇÃO ESPECIAL PARA OS CASOS MAIS DIFÍCEIS</p>
            <div className="ec-special__cols">
              <div>
                <h3>Melasma e manchas teimosas</h3>
                <p>O ácido tranexâmico atua nos mecanismos inflamatórios da pigmentação e ajuda nas manchas que não saem com nada.</p>
              </div>
              <div>
                <h3>Pele sensível com acne</h3>
                <p>A centella asiática acalma a vermelhidão e fortalece a barreira, para tratar a acne sem deixar a pele irritada.</p>
              </div>
            </div>
          </div>
          <Cta />
        </div>
      </section>

      {/* 09 · Chamada (liberte-se) */}
      <section className="ec-section" style={{ background: 'linear-gradient(to right, #fdd9b5, #f8b798)' }}>
        <div className="ec-container ec-split">
          <div className="ec-split__text">
            <p className="ec-eyebrow ec-eyebrow--wine">LIBERTE-SE</p>
            <h2 className="ec-title">
              Nunca foi tão fácil dar <em style={{ color: '#5b2a33' }}>adeus</em> à acne e às manchas
            </h2>
            <p className="ec-body" style={{ color: '#3b2226' }}>
              Um tratamento completo com ativos coreanos de alta performance. A ECLAVE trata, clareia e uniformiza: da espinha de hoje à marca de ontem.
            </p>
            <p className="ec-body" style={{ color: '#3b2226' }}>
              Pele lisa, tom uniforme e autoestima renovada. Comece hoje a sua transformação.
            </p>
            <Cta label="QUERO AGORA" />
          </div>
          <div className="ec-photo" style={{ width: 520, height: 560 }}>
            <img src={photos.i21} alt="Sérum ECLAVE sendo guardado na nécessaire" />
          </div>
        </div>
      </section>

      {/* 10 · Como você usa */}
      <section className="ec-section" style={{ background: '#fff' }}>
        <div className="ec-container ec-center-head">
          <p className="ec-eyebrow">PASSO A PASSO</p>
          <h2 className="ec-title">Como você <em>usa?</em></h2>
          <div className="ec-grid-3" style={{ gap: 28 }}>
            {steps.map(step => (
              <div className="ec-step" key={step.label}>
                <div className="ec-step__photo">
                  <img src={step.photo} alt="" />
                </div>
                <div className="ec-step__text">
                  <p className="ec-step__label">{step.label}</p>
                  <p className="ec-card-title">{step.title}</p>
                  <p className="ec-card-text">{step.text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 11 · Composição (ativos) */}
      <section className="ec-section" style={{ background: '#f7e6dc' }}>
        <div className="ec-container ec-center-head">
          <p className="ec-eyebrow">COMPOSIÇÃO</p>
          <h2 className="ec-title">A ECLAVE é realmente <em>única</em> no mercado</h2>
          <p className="ec-body">
            Enquanto a maioria dos séruns trata só um problema, a ECLAVE foi desenvolvida com tecnologia coreana e ativos que se complementam: uns tratam a acne, outros clareiam as manchas, e todos cuidam da textura da sua pele.
          </p>
          <div className="ec-grid-4">
            {actives.map(a => (
              <div className="ec-active" key={a.name}>
                <span className="ec-num" style={a.small ? { fontSize: 14 } : undefined}>{a.sigla}</span>
                <div className="ec-active__text">
                  <p className="ec-card-title">{a.name}</p>
                  <span className={`ec-badge ${a.tagClass}`}>{a.tag}</span>
                  <p className="ec-card-text">{a.text}</p>
                </div>
              </div>
            ))}
            <div className="ec-active ec-active--dark">
              <span className="ec-num">7</span>
              <div className="ec-active__text">
                <p className="ec-card-title">Fórmula ECLAVE</p>
                <span className="ec-badge ec-badge--gold">FÓRMULA</span>
                <p className="ec-card-text">Sem parabenos, dermatologicamente testada, em embalagem joia de 30 ml.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 12 · Potencialize (kits) */}
      <section className="ec-section" style={{ background: '#fff' }}>
        <div className="ec-container ec-center-head">
          <p className="ec-eyebrow">KITS ECLAVE</p>
          <h2 className="ec-title">Potencialize o seu <em>tratamento</em></h2>
          <p className="ec-body">
            Os kits perfeitos para você. Manchas pedem uso contínuo: com 2 ou 3 frascos, você segue o tratamento por 60 a 90 dias e chega a resultados ainda mais bonitos.
          </p>
          <div className="ec-grid-3" style={{ gap: 28 }}>
            {kitCards.map(card => {
              const k = kits.find(item => item.id === card.kitId)!;
              return (
                <div className={`ec-kitcard${card.kitId === 2 ? ' ec-kitcard--featured' : ''}`} key={card.title}>
                  <div className="ec-kitcard__photo">
                    <img src={card.photo} alt="" />
                    <span className="ec-badge">{card.discount}</span>
                    {card.freeShipping && <span className="ec-badge ec-badge--peach">FRETE GRÁTIS</span>}
                  </div>
                  <div className="ec-kitcard__info">
                    <span className={`ec-badge ${k.badgeClass}`}>{k.badge}</span>
                    <p className="ec-card-title">{card.title}</p>
                    <p className="ec-kitcard__sub">{card.sub}</p>
                    <div className="ec-kitcard__price">
                      <strong>{formatBRL(k.price)}</strong>
                      <span className="ec-old-price">{formatBRL(k.oldPrice)}</span>
                    </div>
                    <p className="ec-kitcard__parcelas">ou 12x de {formatBRL(installment(k.price))} sem juros</p>
                    <Cta label="ADICIONAR" full onClick={() => addToCart(k.id)} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* 13 · Resultados */}
      <section className="ec-section" style={{ background: '#fbf4ec' }}>
        <div className="ec-container ec-split">
          <div className="ec-photo" style={{ width: 520, height: 720 }}>
            <img src={photos.i18} alt="Cliente segurando a caixa da ECLAVE" />
          </div>
          <div className="ec-split__text">
            <p className="ec-eyebrow">RESULTADOS</p>
            <h2 className="ec-title">Resultados visíveis já nas <em>primeiras semanas</em></h2>
            <p className="ec-body">No teste de uso com clientes ECLAVE, depois de 30 dias de uso:</p>
            <div className="ec-results-grid">
              {results.map(text => (
                <div className="ec-result" key={text}>
                  <strong>XX%</strong>
                  <span>{text}</span>
                </div>
              ))}
            </div>
            <p className="ec-note">
              *Percentuais a preencher com o resultado do teste de uso. Os resultados podem variar de pessoa para pessoa.
            </p>
          </div>
        </div>
      </section>

      {/* 14 · Qualidade, segurança e garantia */}
      <section className="ec-section" style={{ background: '#fff' }}>
        <div className="ec-container ec-quality">
          <div className="ec-quality__card">
            <img src={asset('icon-shield-lg.svg')} alt="" width={52} height={52} />
            <p className="ec-eyebrow">QUALIDADE E SEGURANÇA</p>
            <h2 className="ec-title">Fórmula testada e <em>regularizada</em></h2>
            <p className="ec-body">A ECLAVE é dermatologicamente testada e segue as normas da Anvisa para cosméticos. Isso garante:</p>
            <Bullet icon={asset('icon-check-rose.svg')} size={20}>Dermatologicamente testado</Bullet>
            <Bullet icon={asset('icon-check-rose.svg')} size={20}>Sem parabenos</Bullet>
            <Bullet icon={asset('icon-check-rose.svg')} size={20}>Produto regularizado na Anvisa</Bullet>
            <p className="ec-quality__q">O que isso significa?</p>
            <p className="ec-body ec-body--16">
              Que a fórmula foi avaliada para uso direto na pele do rosto, com cada ativo dentro dos limites permitidos. Você trata a acne e as manchas com tranquilidade.
            </p>
          </div>
          <div className="ec-quality__card ec-quality__card--dark">
            <img src={asset('icon-refresh-lg.svg')} alt="" width={52} height={52} />
            <p className="ec-eyebrow ec-eyebrow--gold">GARANTIA</p>
            <h2 className="ec-title ec-title--light">Compre <em>sem medo</em></h2>
            <p className="ec-body ec-body--light">
              Você tem 7 dias de garantia depois de receber o seu ECLAVE. Se não ficar satisfeita, devolvemos o seu dinheiro.
            </p>
            <Bullet icon={asset('icon-check-gold.svg')} size={20} light>Devolução simples e sem burocracia</Bullet>
            <Bullet icon={asset('icon-check-gold.svg')} size={20} light>Atendimento por WhatsApp</Bullet>
            <Bullet icon={asset('icon-check-gold.svg')} size={20} light>Rastreio do pedido em tempo real</Bullet>
          </div>
        </div>
      </section>

      {/* 15 · Avaliações */}
      <section className="ec-section" style={{ background: '#fbf4ec' }}>
        <div className="ec-container" style={{ display: 'flex', flexDirection: 'column', gap: 40 }}>
          <p className="ec-eyebrow">AVALIAÇÕES</p>
          <h2 className="ec-title">O que dizem as <em>clientes ECLAVE</em></h2>
          <div className="ec-reviews">
            <div className="ec-reviews__summary">
              <div className="ec-score">
                <strong>4,9</strong>
                <span>/5</span>
              </div>
              <span className="ec-stars">★★★★★</span>
              <p className="ec-reviews__based">Baseado em 000 avaliações</p>
              <div className="ec-divider" />
              {['Resultados', 'Preço', 'Entrega'].map(label => (
                <div className="ec-subscore" key={label}>
                  <span>{label}</span>
                  <span className="ec-stars">★★★★★</span>
                  <strong>XX%</strong>
                </div>
              ))}
              <button type="button" className="ec-outline-btn">ESCREVER AVALIAÇÃO</button>
            </div>
            <div className="ec-reviews__list">
              <div className="ec-filters">
                {reviewFilters.map(filter => (
                  <button
                    key={filter}
                    type="button"
                    className={`ec-filter${filter === reviewFilter ? ' ec-filter--active' : ''}`}
                    onClick={() => setReviewFilter(filter)}
                  >
                    {filter}
                  </button>
                ))}
              </div>
              <div className="ec-review-grid">
                {visibleReviews.map((review, index) => (
                  <div className="ec-review" key={index}>
                    <div className="ec-review__head">
                      <span className="ec-avatar">NC</span>
                      <div className="ec-review__who">
                        <strong>Nome da cliente</strong>
                        <span>Cidade · data da compra</span>
                      </div>
                      <span className="ec-verified">✓ COMPRA VERIFICADA</span>
                    </div>
                    <span className="ec-stars">★★★★★</span>
                    <p className="ec-review__text">
                      “Depoimento real da cliente entra aqui, contando como estava a pele antes e o que mudou com a ECLAVE.”
                    </p>
                    {review.hasPhotos && (
                      <div className="ec-review__photos">
                        <span className="ec-review__photo">foto</span>
                        <span className="ec-review__photo">foto</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 16 · Instagram */}
      <section className="ec-section" style={{ background: '#fff' }}>
        <div className="ec-container ec-center-head">
          <p className="ec-eyebrow">FIQUE POR DENTRO</p>
          <h2 className="ec-title">Acompanhe a ECLAVE no <em>Instagram</em></h2>
          <p className="ec-body">É por lá que você recebe as novidades, dicas de rotina e os resultados das clientes.</p>
          <div className="ec-insta-grid">
            {instagramPhotos.map((src, index) => (
              <a key={index} href="https://www.instagram.com/eclave" target="_blank" rel="noreferrer">
                <img src={src} alt="" />
              </a>
            ))}
          </div>
          <Cta
            label="VER INSTAGRAM  @ECLAVE"
            onClick={() => window.open('https://www.instagram.com/eclave', '_blank', 'noopener')}
          />
        </div>
      </section>

      {/* 17 · Perguntas frequentes */}
      <section className="ec-section" style={{ background: '#fbf4ec' }} id="duvidas">
        <div className="ec-container ec-center-head">
          <p className="ec-eyebrow">DÚVIDAS</p>
          <h2 className="ec-title">Perguntas <em>frequentes</em></h2>
          <div className="ec-faq">
            {faqs.map((faq, index) => {
              const open = openFaq === index;
              return (
                <div className={`ec-faq__item${open ? ' ec-faq__item--open' : ''}`} key={faq.q}>
                  <button
                    type="button"
                    className="ec-faq__q"
                    aria-expanded={open}
                    onClick={() => setOpenFaq(open ? null : index)}
                  >
                    <span>{faq.q}</span>
                    <span aria-hidden="true">{open ? '−' : '+'}</span>
                  </button>
                  {open && <p className="ec-faq__a">{faq.a}</p>}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* 18 · Chamada final */}
      <section className="ec-section ec-final">
        <div className="ec-container ec-center-head">
          <h2 className="ec-title ec-title--light">Sua pele merece essa <em>chave.</em></h2>
          <p className="ec-body ec-body--light">
            Comece hoje o seu tratamento contra acne e manchas com até 32% OFF e frete grátis nos kits.
          </p>
          <Cta />
          <p className="ec-final__trust">{'✓ Compra 100% segura    ✓ 12x sem juros    ✓ Garantia de 7 dias'}</p>
        </div>
      </section>

      {/* 19 · Rodapé */}
      <footer className="ec-footer" id="rastreio">
        <div className="ec-container">
          <div className="ec-footer__cols">
            <div className="ec-footer__brand">
              <div className="ec-logo ec-logo--footer">
                <span className="ec-logo__name">ECLAVE</span>
                <span className="ec-logo__sub">SKIN</span>
              </div>
              <p>O skincare coreano contra acne e manchas.</p>
            </div>
            <div className="ec-footer__col">
              <h4>NAVEGAR</h4>
              <a href="#inicio">Início</a>
              <a href="#comprar">Produtos</a>
              <a href="#rastreio">Rastreio</a>
              <a href="#duvidas">Dúvidas</a>
            </div>
            <div className="ec-footer__col">
              <h4>ATENDIMENTO</h4>
              <span>WhatsApp: (00) 00000-0000</span>
              <a href="mailto:contato@eclave.com.br">contato@eclave.com.br</a>
              <span>Seg. a sex., 9h às 18h</span>
            </div>
            <div className="ec-footer__col">
              <h4>INSTITUCIONAL</h4>
              <span>Políticas de pagamento</span>
              <span>Trocas e devoluções</span>
              <span>Política de privacidade</span>
            </div>
          </div>
          <div className="ec-footer__divider" />
          <p className="ec-footer__legal">
            ECLAVE · CNPJ 00.000.000/0001-00 · Endereço da empresa · © 2026 Todos os direitos reservados. Os resultados podem variar de pessoa para pessoa.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default EclavePage;
