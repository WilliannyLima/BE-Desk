// Profile app - uses React (assumes React and ReactDOM are loaded globally)
(function(){
  const e = React.createElement;

  function useApi(url){
    const [data, setData] = React.useState(null);
    const [loading, setLoading] = React.useState(true);
    const [error, setError] = React.useState(null);

    React.useEffect(()=>{
      let mounted = true;
      setLoading(true);
      axios.get(url).then(res=>{
        if(!mounted) return;
        setData(res.data.data);
      }).catch(err=>{
        setError(err);
      }).finally(()=>mounted && setLoading(false));

      return ()=> mounted = false;
    }, [url]);

    return {data, loading, error};
  }

  const AVATAR_PLACEHOLDER = '/static/img/avatar-placeholder.png';

  function Avatar({src, name}){
    return e('div', {className: 'avatar-frame inline-block rounded-full p-1 bg-gradient-to-tr from-gray-800 to-black'},
      e('img', {src: src || AVATAR_PLACEHOLDER, alt: name, className: 'w-28 h-28 rounded-full object-cover border-2 border-transparent'})
    );
  }

  function StatCard({icon, label, value}){
    return e('div', {className: 'glass-card p-4 flex items-center gap-4'},
      e('div', {className: 'p-3 rounded-lg bg-black/30'}, icon),
      e('div', null, e('div', {className:'text-sm text-gray-300'}, label), e('div', {className:'text-xl font-semibold text-white'}, value))
    )
  }

  function ProfileRoot(){
    // prefer local integracao endpoint if available
    const endpoint = '/api/rh/eu/';
    const {data, loading, error} = useApi(endpoint);

    if(loading) return e('div', {className:'animate-pulse'}, e('div', {className:'h-8 bg-gray-700 rounded w-1/3 mb-4'}), e('div', {className:'grid grid-cols-3 gap-4'}, e('div', {className:'h-24 bg-gray-800 rounded col-span-1'}), e('div', {className:'h-24 bg-gray-800 rounded col-span-2'})));

    if(error) return e('div', {className:'text-red-400'}, 'Erro ao carregar os dados.')

    const u = data || {};

    return e('div', {className:'space-y-6'},
      e('div', {className:'profile-banner p-6 glass-card flex flex-col md:flex-row items-center gap-6'},
        e('div', {className:'flex items-center gap-6 flex-1'},
          e(Avatar, {src: u.foto, name: u.nome}),
          e('div', null,
            e('div', {className:'text-2xl font-bold text-white'}, u.nome || 'Usuário'),
            e('div', {className:'text-sm text-gray-300 mt-1'}, e('span', {className:'inline-block mr-3'}, 'ID: ' + (u.matricula || '—')), e('span', {className:'inline-block bg-green-600 text-white px-2 py-0.5 rounded-full text-xs ml-2'}, 'Institucional'))
          )
        ),
        e('div', {className:'flex gap-3'},
          e('button', {className:'px-4 py-2 bg-gray-800 text-white rounded hover:bg-gray-700'}, 'Editar Perfil'),
          e('button', {className:'px-4 py-2 bg-transparent border border-gray-700 text-gray-200 rounded hover:bg-gray-900'}, 'Alterar Senha')
        )
      ),

      e('div', {className:'grid grid-cols-1 lg:grid-cols-3 gap-6'},
        e('div', {className:'space-y-4 lg:col-span-2'},
          e('div', {className:'glass-card p-6'},
            e('h3', {className:'text-xl font-semibold text-white mb-4'}, 'Informações Pessoais'),
            e('div', {className:'grid grid-cols-1 md:grid-cols-2 gap-3'},
              e('div', {className:'text-sm text-gray-300'}, e('div', {className:'font-semibold text-white'}, 'Nome completo'), e('div', null, u.nome || '—')),
              e('div', {className:'text-sm text-gray-300'}, e('div', {className:'font-semibold text-white'}, 'E-mail'), e('div', null, u.email || '—')),
              e('div', {className:'text-sm text-gray-300'}, e('div', {className:'font-semibold text-white'}, 'Matrícula'), e('div', null, u.matricula || '—')),
              e('div', {className:'text-sm text-gray-300'}, e('div', {className:'font-semibold text-white'}, 'Campus'), e('div', null, u.campus || '—')),
              e('div', {className:'text-sm text-gray-300'}, e('div', {className:'font-semibold text-white'}, 'Curso'), e('div', null, u.curso || '—')),
              e('div', {className:'text-sm text-gray-300'}, e('div', {className:'font-semibold text-white'}, 'Vínculo'), e('div', null, u.vinculo || '—'))
            )
          ),

          e('div', {className:'glass-card p-6'},
            e('h3', {className:'text-xl font-semibold text-white mb-4'}, 'Atividades Recentes'),
            e('div', {className:'text-sm text-gray-300'}, 'Sem atividades recentes.')
          )
        ),

        e('div', {className:'space-y-4'},
          e('div', {className:'glass-card p-6'},
            e('h4', {className:'text-lg font-semibold text-white mb-3'}, 'Estatísticas'),
            e('div', {className:'grid grid-cols-2 gap-3'},
              e(StatCard, {icon: e('span', null, '📅'), label:'Reservas', value:'12'}),
              e(StatCard, {icon: e('span', null, '⏱️'), label:'Horas', value:'48h'})
            )
          ),

          e('div', {className:'glass-card p-6'},
            e('h4', {className:'text-lg font-semibold text-white mb-3'}, 'Segurança'),
            e('div', {className:'flex flex-col gap-3'},
              e('div', {className:'flex items-center justify-between text-sm text-gray-300'}, e('div', null, 'Autenticação'), e('div', {className:'text-white'}, 'SUAP')),
              e('div', {className:'flex items-center justify-between text-sm text-gray-300'}, e('div', null, 'Último acesso'), e('div', {className:'text-white'}, '—')),
              e('div', {className:'flex gap-2'}, e('button', {className:'px-3 py-1 bg-red-600 text-white rounded'}, 'Encerrar Sessões'), e('button', {className:'px-3 py-1 border border-gray-700 text-white rounded'}, 'Ativar 2FA'))
            )
          )
        )
      )
    );
  }

  document.addEventListener('DOMContentLoaded', function(){
    if(document.getElementById('profile-root')){
      ReactDOM.createRoot(document.getElementById('profile-root')).render(React.createElement(ProfileRoot));
    }
  });

})();
